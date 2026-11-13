# MotorScan

Sistema web que detecta **fallas en motores de motocicletas a partir de su sonido**. El usuario graba o sube un audio del motor en ralentí. El sistema lo convierte en un **espectrograma de Mel** y una **red neuronal convolucional (CNN)** clasifica el motor como `normal` o `anomalia`, con un porcentaje de confianza.

---

## Contenido

- [Funcionalidades](#funcionalidades)
- [Arquitectura y tecnologías](#arquitectura-y-tecnologías)
- [Estructura del repositorio](#estructura-del-repositorio)
- [1. Ejecutar en local](#1-ejecutar-en-local-docker-compose)
- [2. Desplegar en un servidor (EC2)](#2-desplegar-en-un-servidor-ec2-con-https)
- [3. Desplegar en Kubernetes (k3s)](#3-desplegar-en-kubernetes-k3s)
- [Variables de entorno](#variables-de-entorno)
- [Pruebas](#pruebas)
- [Base de datos](#base-de-datos)
- [Actualizar el modelo CNN](#actualizar-el-modelo-cnn)
- [Documentación adicional](#documentación-adicional)

---

## Funcionalidades

- Inicio de sesión con **Google** (OAuth 2.0) y sesión con **JWT**.
- Formulario con los datos de la moto (marca, modelo, cilindraje, año, kilometraje) para acotar el análisis.
- **Grabación** desde el micrófono o **carga** de un archivo de audio (wav, mp3, m4a, webm…).
- Diagnóstico con la CNN: resultado, confianza e imagen del espectrograma.
- **Historial** de diagnósticos por usuario y vista de detalle.
- Encuesta de confianza del usuario y registro del **veredicto del mecánico**.
- **Panel de investigación** (`/admin`) con métricas: exactitud real, detección temprana y confianza antes/después.

**Privacidad:** el audio no se almacena. Se procesa en memoria y solo se guarda la imagen del espectrograma.

---

## Arquitectura y tecnologías

```
Navegador ──► Proxy / Ingress (HTTPS)
                 ├── /      → Frontend: React + TypeScript + Vite + MUI (servido por nginx)
                 └── /api/  → Backend:  FastAPI + SQLAlchemy + Alembic
                                  ├── CNN: TensorFlow/Keras + librosa (espectrograma de Mel)
                                  └── Base de datos: SQLite (local/EC2) o PostgreSQL (Kubernetes)
```

| Capa | Tecnología |
|---|---|
| Frontend | React 19, TypeScript, Vite, Material UI, MUI X Charts |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PyJWT |
| IA | TensorFlow (CPU), Keras, librosa, ffmpeg, Pillow |
| Datos | SQLite / PostgreSQL 16 |
| Infraestructura | Docker, Docker Compose, nginx, Let's Encrypt, Kubernetes (k3s), Traefik, cert-manager |
| CI | GitHub Actions → GitHub Container Registry (GHCR) |

---

## Estructura del repositorio

```
.
├── backend/                 API FastAPI
│   ├── main.py              Punto de entrada (carga y calienta el modelo CNN)
│   ├── routers/             Endpoints (auth, diagnósticos, catálogo, admin)
│   ├── services/            Lógica de negocio y servicio CNN
│   ├── crud/  models/  schemas/
│   ├── alembic/             Migraciones de la base de datos
│   ├── modelos/             Modelo CNN (.keras) + model_config.json
│   ├── tests/               Pruebas unitarias, funcionales y no funcionales (pytest)
│   ├── seed.py              Catálogo inicial (marcas, modelos, CNN)
│   └── .env.example         Plantilla de variables de entorno
├── frontend/                SPA React (Vite) + nginx
├── reverse/                 Configuración del reverse proxy nginx (EC2 y local)
├── k8s/                     Manifiestos de Kubernetes (kustomize)
├── .github/workflows/       CI: construcción y publicación de imágenes
├── docker-compose.yml       Despliegue en servidor (HTTPS)
├── docker-compose.local.yml Ajustes para localhost
└── manuales/                Manual técnico y manual de usuario
```

---

## 1. Ejecutar en local (Docker Compose)

**Requisitos:** Docker y Docker Compose v2.

```bash
git clone https://github.com/rramirezg18/pg-analisisdesonidos.git
cd pg-analisisdesonidos

# 1. Variables de entorno
cp backend/.env.example backend/.env
```

Edita `backend/.env` con estos valores para localhost:

```env
SECRET_KEY=<genera uno: python3 -c "import secrets; print(secrets.token_hex(32))">
CORS_ORIGINS=http://localhost,http://localhost:5173
FRONTEND_URL=http://localhost
GOOGLE_CLIENT_ID=<tu client id>
GOOGLE_CLIENT_SECRET=<tu client secret>
GOOGLE_CALLBACK_URL=http://localhost/api/auth/google/callback
ADMIN_EMAILS=<tu correo, para entrar al panel /admin>
```

Para obtener las credenciales de Google, crea un *ID de cliente de OAuth* (tipo *Aplicación web*) en <https://console.cloud.google.com/apis/credentials> y agrega `http://localhost/api/auth/google/callback` como URI de redireccionamiento autorizado.

```bash
# 2. Levantar los contenedores
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build

# 3. Cargar el catálogo (marcas, modelos y CNN). Se hace una sola vez.
docker compose exec backend python seed.py
```

| Qué | URL |
|---|---|
| Aplicación | http://localhost |
| API | http://localhost/api/ |
| Swagger (solo en local) | http://localhost/api/docs |

Comandos útiles:

```bash
docker compose logs -f backend      # ver logs
docker compose down                 # detener (los datos se conservan en backend/data)
```

El primer arranque tarda unos 30–60 s, porque el backend aplica las migraciones, carga TensorFlow y hace un análisis de prueba para que el primer diagnóstico real sea rápido.

---

## 2. Desplegar en un servidor (EC2) con HTTPS

**Requisitos:** un servidor Linux con Docker, los puertos 80 y 443 abiertos y un dominio apuntando a su IP (por ejemplo, DuckDNS).

```bash
git clone https://github.com/rramirezg18/pg-analisisdesonidos.git
cd pg-analisisdesonidos
cp backend/.env.example backend/.env       # completar con las URLs https:// del dominio
```

1. **Certificado de Let's Encrypt** (en el host, una sola vez):
   ```bash
   sudo apt install -y certbot
   sudo certbot certonly --standalone -d <tu-dominio>
   ```
2. Reemplaza el dominio que aparece en `reverse/nginx.conf` (`server_name` y rutas del certificado) por `<tu-dominio>`.
3. Levanta los contenedores y carga el catálogo:
   ```bash
   docker compose up -d --build
   docker compose exec backend python seed.py
   ```

**Para actualizar a una versión nueva:**
```bash
git pull
docker compose up -d --build
```

En este modo la base es SQLite, en `backend/data/sonidos_motos.db`, y los espectrogramas están en `backend/data/espectrogramas/`. Para respaldar, copia la carpeta `backend/data/`.

---

## 3. Desplegar en Kubernetes (k3s)

Los manifiestos están en `k8s/` y se aplican con **kustomize** (incluido en `kubectl`).

```
Internet ──► Ingress Traefik (HTTPS, cert-manager)
               └─► Service frontend ──► Pods frontend (nginx: SPA + proxy /api)
                                            └─► Service backend ──► Pods backend (FastAPI + CNN)
                                                                       ├─► Service postgres ──► StatefulSet PostgreSQL + PVC
                                                                       └─► PVC espectrogramas
```

| Archivo | Recurso |
|---|---|
| `kustomization.yaml` | Namespace, imágenes, Secret y ConfigMap generados |
| `backend-deployment.yaml` | Deployment del backend: probes, recursos, RollingUpdate |
| `frontend-deployment.yaml` | Deployment del frontend |
| `postgres.yaml` | StatefulSet + Service de PostgreSQL |
| `backend-service.yaml`, `frontend-service.yaml` | Services internos (ClusterIP) |
| `backend-configmap.yaml` | Configuración no sensible |
| `backend-secret.env.example` | Plantilla de los secretos (el `.env` real no se versiona) |
| `backend-pvc.yaml` | Volumen de los espectrogramas |
| `ingress.yaml`, `issuer.yaml` | Entrada pública y certificado HTTPS de Let's Encrypt |
| `nginx/default.conf` | nginx del frontend dentro del clúster |
| `autoescalado/` | HPA opcional (autoescalado por CPU) |

### 3.1 Imágenes

Las imágenes las construye **GitHub Actions** (`.github/workflows/imagenes.yml`) en cada push a `main` que modifique `backend/` o `frontend/`, y las publica en:

- `ghcr.io/rramirezg18/motorscan-backend:<versión>`
- `ghcr.io/rramirezg18/motorscan-frontend:<versión>`

También se puede ejecutar a mano desde la pestaña **Actions → Imagenes Docker → Run workflow**. Los paquetes de GHCR deben ser **públicos** para que el clúster pueda descargarlos.

### 3.2 Primer despliegue

```bash
# 1. Secretos (este archivo no se sube a git)
cp k8s/backend-secret.env.example k8s/backend-secret.env
#    POSTGRES_PASSWORD  -> python3 -c "import secrets; print(secrets.token_hex(16))"
#    SECRET_KEY         -> python3 -c "import secrets; print(secrets.token_hex(32))"
#    GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / ADMIN_EMAILS

# 2. Aplicar todos los manifiestos
kubectl apply -k k8s/

# 3. Esperar a que todo esté listo
kubectl rollout status statefulset/postgres
kubectl rollout status deploy/backend --timeout=5m
kubectl rollout status deploy/frontend

# 4. Cargar el catálogo (una sola vez)
kubectl exec deploy/backend -- python seed.py

# 5. Verificar
kubectl get pods,svc,ingress,pvc,certificate
```

Si usas otro dominio o namespace, cámbialo en `k8s/ingress.yaml`, `k8s/backend-configmap.yaml` y `namespace:` de `k8s/kustomization.yaml`. Registra también la URL de callback en Google: `https://<dominio>/api/auth/google/callback`.

### 3.3 Publicar una versión nueva

1. Sube la versión en `.github/workflows/imagenes.yml` (`VERSION`) **y** en `k8s/kustomization.yaml` (`newTag`), por ejemplo a `1.0.2`. No reutilices una etiqueta: los nodos guardan las imágenes en caché.
2. Haz commit y push a `main`, y espera a que el workflow termine en verde.
3. Aplica:
   ```bash
   kubectl apply -k k8s/
   ```
   La actualización es **sin caída**: los pods nuevos arrancan antes de que se apaguen los viejos.

### 3.4 Escalado y resiliencia

```bash
# Escalar manualmente
kubectl scale deployment backend --replicas=3
kubectl scale deployment frontend --replicas=3
kubectl get pods -w

# Autorrecuperación: borrar un pod y ver cómo se recrea solo
kubectl delete pod <nombre-del-pod>

# Volver a la versión anterior
kubectl rollout undo deployment/backend

# Autoescalado por CPU (opcional; mientras esté activo, `kubectl scale` se revierte)
kubectl apply -k k8s/autoescalado/
kubectl delete -k k8s/autoescalado/
```

El backend escala porque todas las réplicas comparten la base PostgreSQL. Las migraciones usan un *advisory lock* para que solo una réplica las ejecute a la vez, y la sesión es JWT, sin estado en memoria. Las réplicas comparten el volumen de espectrogramas en el mismo nodo.

### 3.5 Conectarse a la base de datos (DBeaver, psql)

```bash
kubectl port-forward svc/postgres 5433:5432
```

Conéctate a `localhost:5433` con la base `motorscan`, el usuario `motorscan` y la contraseña `POSTGRES_PASSWORD` del Secret.

---

## Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DATABASE_URL` | Conexión SQLAlchemy | `sqlite:////app/data/sonidos_motos.db` o `postgresql+psycopg2://…` |
| `SECRET_KEY` | Clave para firmar los JWT | valor aleatorio de 64 caracteres |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración de la sesión | `60` |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma) | `https://<tu-dominio>` |
| `FRONTEND_URL` | URL a la que vuelve el login | `https://<tu-dominio>` |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Credenciales OAuth de Google | |
| `GOOGLE_CALLBACK_URL` | Callback registrada en Google | `https://<dominio>/api/auth/google/callback` |
| `ADMIN_EMAILS` | Correos con acceso al panel `/admin` | `a@x.com,b@y.com` |
| `ADMIN_API_KEY` | Clave (header `X-Admin-Key`) para escribir en el catálogo | vacío = deshabilitado |
| `ANALISIS_POR_MINUTO` | Límite de análisis por usuario por minuto | `10` |
| `HABILITAR_DOCS` | Mostrar Swagger en `/api/docs` | `false` en producción |
| `CALENTAR_MODELO` | Hacer un análisis de prueba al arrancar | `true` |

---

## Pruebas

Las pruebas usan una base SQLite temporal, nunca la de producción.

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest
python -m pytest -q
```

También se pueden correr sin instalar nada, dentro de la imagen del backend:

```bash
docker compose build backend
docker run --rm \
  -v "$PWD/backend/tests:/app/tests:ro" -v "$PWD/backend/pytest.ini:/app/pytest.ini:ro" \
  pg-analisisdesonidos-backend sh -c "pip install -q pytest && python -m pytest -q"
```

Hay pruebas unitarias, funcionales (CP-01…CP-10) y no funcionales: rendimiento menor de 10 s, seguridad y validaciones.

---

## Base de datos

| Tabla | Contenido |
|---|---|
| `usuario` | Usuarios autenticados por OAuth |
| `marca`, `modelo` | Catálogo de motos (el cilindraje es entrada del CNN) |
| `modelo_cnn` | Versiones del modelo de IA (solo una activa) |
| `diagnostico` | Cada análisis: resultado, confianza, espectrograma, veredicto del mecánico |
| `evaluacion_usuario` | Encuesta de confianza antes/después (escala Likert 1–5) |

Relaciones: `marca 1─N modelo 1─N diagnostico N─1 usuario`, `modelo_cnn 1─N diagnostico`, `diagnostico 1─0..1 evaluacion_usuario`.

El esquema se crea y actualiza automáticamente con **Alembic** al iniciar el backend.

---

## Actualizar el modelo CNN

El modelo se entrena aparte (Google Colab) y se reemplaza sin tocar código:

1. Sustituye `backend/modelos/modelo_cnn_v1.keras` y, si cambió el preprocesamiento, `backend/modelos/model_config.json`.
2. Despliega de nuevo:
   - **Local / EC2:** `docker compose up -d --build backend`
   - **Kubernetes:** sube la versión y haz push (ver [3.3](#33-publicar-una-versión-nueva)).

---

## Documentación adicional

- [Manual técnico](manuales/manual_tecnico.md)
- [Manual de usuario](manuales/manual_usuario.md)
