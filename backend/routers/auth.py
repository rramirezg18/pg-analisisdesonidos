import os
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas.usuario import UsuarioCreate
import services.usuario as service_usuario
from utils.security import crear_token_acceso

router = APIRouter(prefix="/auth", tags=["Auth"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_CALLBACK_URL = os.getenv(
    "GITHUB_CALLBACK_URL", "http://localhost/api/auth/github/callback"
)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_CALLBACK_URL = os.getenv(
    "GOOGLE_CALLBACK_URL", "http://localhost/api/auth/google/callback"
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost")

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER = "https://api.github.com/user"
GITHUB_API_EMAILS = "https://api.github.com/user/emails"

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_API_USERINFO = "https://openidconnect.googleapis.com/v1/userinfo"


def _validar_state(request: Request, state: str) -> None:
    state_cookie = request.cookies.get("oauth_state")
    if not state_cookie or state_cookie != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State inválido (posible CSRF)",
        )


def _redirigir_con_state(url_autorizacion: str, params: dict) -> RedirectResponse:
    """Redirige al proveedor guardando el state en cookie httpOnly (anti-CSRF)."""
    state = secrets.token_urlsafe(16)
    params = {**params, "state": state}
    respuesta = RedirectResponse(f"{url_autorizacion}?{urlencode(params)}")
    respuesta.set_cookie(
        "oauth_state", state, httponly=True, max_age=600, samesite="lax"
    )
    return respuesta


def _redirigir_al_frontend(db: Session, identidad: UsuarioCreate) -> RedirectResponse:
    """Upsert del usuario, firma NUESTRO JWT y lo manda al frontend."""
    usuario = service_usuario.login_oauth(db, identidad)
    jwt_token = crear_token_acceso({"sub": str(usuario.id_usuario)})
    redireccion = RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={jwt_token}")
    redireccion.delete_cookie("oauth_state")
    return redireccion


@router.get("/github/login")
def github_login():
    """Paso 1: redirige al usuario a GitHub para que autorice."""
    return _redirigir_con_state(
        GITHUB_AUTHORIZE_URL,
        {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": GITHUB_CALLBACK_URL,
            "scope": "read:user user:email",
        },
    )


@router.get("/github/callback")
def github_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Paso 3-4: valida state, intercambia code, hace upsert del usuario y firma el JWT."""
    _validar_state(request, state)

    with httpx.Client(timeout=10) as client:
        # code -> access token de GitHub
        token_resp = client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_CALLBACK_URL,
            },
        )
        gh_access_token = token_resp.json().get("access_token")
        if not gh_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub no devolvió un access token",
            )

        headers = {
            "Authorization": f"Bearer {gh_access_token}",
            "Accept": "application/vnd.github+json",
        }
        gh_user = client.get(GITHUB_API_USER, headers=headers).json()

        # El email puede venir null si es privado; lo pedimos aparte.
        email = gh_user.get("email")
        if not email:
            emails = client.get(GITHUB_API_EMAILS, headers=headers).json()
            email = next(
                (e["email"] for e in emails if e.get("primary")),
                emails[0]["email"] if emails else None,
            )

    identidad = UsuarioCreate(
        proveedor_oauth="github",
        id_externo_proveedor=str(gh_user["id"]),
        email=email
        or f"{gh_user['id']}+{gh_user['login']}@users.noreply.github.com",
        nombre=gh_user.get("name") or gh_user.get("login"),
    )
    return _redirigir_al_frontend(db, identidad)


@router.get("/google/login")
def google_login():
    """Paso 1: redirige al usuario a Google para que autorice."""
    return _redirigir_con_state(
        GOOGLE_AUTHORIZE_URL,
        {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_CALLBACK_URL,
            "response_type": "code",
            "scope": "openid email profile",
            "prompt": "select_account",
        },
    )


@router.get("/google/callback")
def google_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Paso 3-4: valida state, intercambia code, hace upsert del usuario y firma el JWT."""
    _validar_state(request, state)

    with httpx.Client(timeout=10) as client:
        # code -> access token de Google (a diferencia de GitHub, exige grant_type)
        token_resp = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GOOGLE_CALLBACK_URL,
                "grant_type": "authorization_code",
            },
        )
        google_access_token = token_resp.json().get("access_token")
        if not google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google no devolvió un access token",
            )

        google_user = client.get(
            GOOGLE_API_USERINFO,
            headers={"Authorization": f"Bearer {google_access_token}"},
        ).json()

    # "sub" es el id estable del usuario en Google (no cambia aunque cambie el email).
    if not google_user.get("sub") or not google_user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google no devolvió un email verificado",
        )

    identidad = UsuarioCreate(
        proveedor_oauth="google",
        id_externo_proveedor=google_user["sub"],
        email=google_user["email"],
        nombre=google_user.get("name") or google_user["email"].split("@")[0],
    )
    return _redirigir_al_frontend(db, identidad)
