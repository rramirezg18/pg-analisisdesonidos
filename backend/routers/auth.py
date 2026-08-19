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
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost")

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER = "https://api.github.com/user"
GITHUB_API_EMAILS = "https://api.github.com/user/emails"


@router.get("/github/login")
def github_login():
    """Paso 1: redirige al usuario a GitHub para que autorice."""
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_CALLBACK_URL,
        "scope": "read:user user:email",
        "state": state,
    }
    respuesta = RedirectResponse(f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}")
    # Guardamos el state en cookie httpOnly para verificarlo en el callback (anti-CSRF).
    respuesta.set_cookie(
        "oauth_state", state, httponly=True, max_age=600, samesite="lax"
    )
    return respuesta


@router.get("/github/callback")
def github_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Paso 3-4: valida state, intercambia code, hace upsert del usuario y firma el JWT."""
    state_cookie = request.cookies.get("oauth_state")
    if not state_cookie or state_cookie != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State inválido (posible CSRF)",
        )

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
    usuario = service_usuario.login_oauth(db, identidad)

    # Firmamos NUESTRO JWT (no el de GitHub) y lo mandamos al frontend.
    jwt_token = crear_token_acceso({"sub": str(usuario.id_usuario)})
    redireccion = RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={jwt_token}")
    redireccion.delete_cookie("oauth_state")
    return redireccion
