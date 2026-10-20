# Manual técnico de MotorScan

**Sistema de detección de fallas en motores de motocicleta mediante análisis de sonido**

Documentación técnica de arquitectura, instalación, despliegue y mantenimiento, elaborada según las normas ISO/IEC/IEEE 15289:2019 e ISO/IEC/IEEE 26514:2022.

## Identificación del documento

| Campo                 | Valor                                                          |
|-----------------------|----------------------------------------------------------------|
| Código del documento  | MS-MT-001                                                      |
| Versión del documento | 1.0                                                            |
| Versión del software  | MotorScan 1.0 (modelo CNN v1.0)                                |
| Fecha de emisión      | 20 de octubre de 2026                                          |
| Estado                | Emitido                                                        |
| Tipo de documento     | Manual técnico (descripción de diseño, instalación y operación) |
| Normas de referencia  | ISO/IEC/IEEE 15289:2019; ISO/IEC/IEEE 26514:2022               |
| Autor                 | Roberto Ramírez                                                |
| Contexto              | Proyecto de graduación                                         |
| Repositorio           | https://github.com/rramirezg18/pg-analisisdesonidos            |

## Historial de revisiones

| Versión | Fecha      | Autor           | Descripción del cambio         |
|---------|------------|-----------------|--------------------------------|
| 1.0     | 20/10/2026 | Roberto Ramírez | Emisión inicial del documento. |

<div style="page-break-after: always;"></div>

## Índice de contenido

1. Introducción
   - 1.1 Propósito
   - 1.2 Alcance
   - 1.3 Audiencia
   - 1.4 Convenciones
   - 1.5 Documentos de referencia
2. Descripción general del sistema
   - 2.1 Arquitectura
   - 2.2 Flujo de un diagnóstico
   - 2.3 Tecnologías utilizadas
   - 2.4 Estructura del repositorio
3. Backend
   - 3.1 Organización en capas
   - 3.2 Punto de entrada y ciclo de vida
   - 3.3 Middleware y manejo de errores
   - 3.4 Catálogo de endpoints
   - 3.5 Almacenamiento de espectrogramas
4. Autenticación y autorización
   - 4.1 Flujo OAuth 2.0
   - 4.2 Token JWT
   - 4.3 Registro y vinculación de usuarios
5. Módulo de inteligencia artificial
   - 5.1 Modelo CNN
   - 5.2 Archivo de configuración del modelo
   - 5.3 Preprocesamiento del audio
   - 5.4 Inferencia y cálculo de la confianza
   - 5.5 Reemplazo del modelo
6. Base de datos
   - 6.1 Motor y conexión
   - 6.2 Modelo de datos
   - 6.3 Migraciones
   - 6.4 Datos iniciales (seed)
7. Frontend
   - 7.1 Estructura
   - 7.2 Rutas
   - 7.3 Gestión de la sesión
   - 7.4 Comunicación con la API
8. Configuración
   - 8.1 Variables de entorno del backend
   - 8.2 Variables de entorno del frontend
9. Instalación del entorno de desarrollo
10. Despliegue en producción
11. Operación y mantenimiento
12. Seguridad
13. Solución de problemas
14. Limitaciones conocidas y trabajo futuro
15. Glosario
16. Soporte y contacto

- Anexo A. Referencia rápida de comandos
- Anexo B. Correspondencia con ISO/IEC/IEEE 15289

<div style="page-break-after: always;"></div>

## 1. Introducción

### 1.1 Propósito

Este manual describe la arquitectura interna de MotorScan y los procedimientos necesarios para instalarlo, configurarlo, desplegarlo y mantenerlo. Su objetivo es que una persona con conocimientos técnicos pueda comprender el sistema, ponerlo en funcionamiento en un servidor nuevo y realizar cambios sobre el código.

### 1.2 Alcance

El manual cubre:

- La arquitectura del sistema y la responsabilidad de cada componente.
- El diseño del backend, del frontend, de la base de datos y del módulo de inteligencia artificial.
- La configuración mediante variables de entorno.
- La instalación del entorno de desarrollo.
- El despliegue en producción con Docker, Nginx y HTTPS sobre Amazon EC2.
- Las tareas de operación: actualización, respaldo, renovación del certificado y revisión de registros.
- La solución de los problemas más frecuentes.

Quedan fuera del alcance el uso de la aplicación por parte del usuario final, documentado en el *Manual de usuario* (MS-MU-001), y el proceso de recolección de datos y entrenamiento del modelo CNN.

### 1.3 Audiencia

Este manual está dirigido a:

- **Desarrolladores** que mantienen o amplían el código.
- **Administradores de sistemas** que despliegan y operan el servidor.
- **Evaluadores técnicos** del proyecto de graduación.

Se asumen conocimientos de Linux, línea de comandos, Git, Docker, HTTP/REST, Python y TypeScript/React.

### 1.4 Convenciones

| Convención              | Significado                                                       | Ejemplo                       |
|-------------------------|-------------------------------------------------------------------|-------------------------------|
| `Texto monoespaciado`   | Comando, ruta de archivo, variable, endpoint o fragmento de código. | `docker compose ps`           |
| `MAYÚSCULAS_CON_GUION`  | Variable de entorno.                                              | `SECRET_KEY`                  |
| `<valor>`               | Valor que debe sustituirse por uno real.                          | `<TU_DOMINIO>`                |
| Bloque de código        | Comandos que se ejecutan en una terminal, en el orden mostrado.   |                               |

Las rutas de archivo son relativas a la raíz del repositorio, salvo que se indique lo contrario. Los endpoints de la API se escriben sin el prefijo `/api`, que agrega el proxy inverso (ver sección 2.1).

> **PRECAUCIÓN:** acción que puede producir pérdida de datos, interrupción del servicio o un riesgo de seguridad.

> **NOTA:** información complementaria.

### 1.5 Documentos de referencia

- MS-MU-001, *Manual de usuario de MotorScan*.
- DERCAS v1.0, *Documento de Especificación de Requerimientos y Criterios de Aceptación de Software* (carpeta `dercas/`).
- ISO/IEC/IEEE 15289:2019, *Systems and software engineering — Content of life-cycle information items (documentation)*.
- ISO/IEC/IEEE 26514:2022, *Systems and software engineering — Design and development of information for users*.
- RFC 6749, *The OAuth 2.0 Authorization Framework*.
- RFC 7519, *JSON Web Token (JWT)*.

<div style="page-break-after: always;"></div>

## 2. Descripción general del sistema

### 2.1 Arquitectura

MotorScan es una aplicación web de tres contenedores Docker orquestados con Docker Compose. Un proxy inverso Nginx es el único punto de entrada público y reparte las peticiones entre el frontend y el backend según la ruta.

```
                          Internet
                             │
                  HTTP :80 / HTTPS :443
                             │
                ┌────────────▼────────────┐
                │  proxy (nginx:1.27)     │  reverse/nginx.conf
                │  - TLS (Let's Encrypt)  │  Certificados en /etc/letsencrypt
                │  - 80 → 301 a HTTPS     │  (montado desde el host)
                └──────┬───────────┬──────┘
           /  (resto)  │           │  /api/*  (se elimina el prefijo)
                ┌──────▼─────┐ ┌───▼──────────────────────┐
                │ frontend   │ │ backend (FastAPI)        │
                │ nginx :80  │ │ uvicorn :8001            │
                │ React SPA  │ │ - API REST               │
                │ (estático) │ │ - Modelo CNN (Keras)     │
                └────────────┘ │ - ffmpeg + librosa       │
                               └───┬──────────────────┬───┘
                                   │                  │
                     ./backend/data (volumen)   ./backend/modelos (volumen)
                     - sonidos_motos.db         - modelo_cnn_v1.keras
                     - espectrogramas/*.png     - model_config.json

        Servicios externos: Google OAuth 2.0 / OpenID Connect, GitHub OAuth
```

| Contenedor | Imagen / build        | Puerto interno | Publicado en el host | Responsabilidad                                               |
|------------|-----------------------|----------------|----------------------|---------------------------------------------------------------|
| `proxy`    | `nginx:1.27-alpine`   | 80, 443        | 80, 443              | Terminación TLS, redirección a HTTPS y enrutamiento.          |
| `frontend` | `./frontend`          | 80             | No                   | Servir la SPA de React compilada.                             |
| `backend`  | `./backend`           | 8001           | No                   | API REST, autenticación, inferencia del CNN y persistencia.   |

Como el frontend y la API se sirven desde el mismo origen, el navegador no realiza peticiones entre orígenes en producción. La configuración de CORS solo es necesaria en el entorno de desarrollo.

### 2.2 Flujo de un diagnóstico

1. El usuario inicia sesión con Google o GitHub y el frontend guarda el JWT emitido por el backend.
2. En el asistente de diagnóstico, el usuario selecciona marca, modelo y año, y graba o sube el audio del motor.
3. El frontend envía el audio y los datos de la moto a `POST /diagnosticos/analizar` como `multipart/form-data`.
4. El backend valida el formato y el tamaño, convierte el audio a WAV con ffmpeg y genera el espectrograma de Mel con librosa.
5. El CNN recibe el espectrograma y el cilindraje normalizado, y devuelve un valor entre 0 y 1.
6. El backend clasifica el resultado (`normal` o `anomalia`), calcula la confianza, guarda la imagen PNG del espectrograma y registra el diagnóstico en la base de datos.
7. El frontend muestra el resultado y el espectrograma.

> **NOTA:** el audio nunca se escribe en disco ni en la base de datos. Solo se procesa en memoria y se conserva la imagen del espectrograma.

### 2.3 Tecnologías utilizadas

| Capa                 | Tecnología                         | Versión            |
|----------------------|------------------------------------|--------------------|
| Lenguaje backend     | Python                             | 3.12               |
| Framework web        | FastAPI                            | 0.141.1            |
| Servidor ASGI        | Uvicorn                            | 0.52.3             |
| ORM                  | SQLAlchemy                         | 2.0.52             |
| Migraciones          | Alembic                            | 1.19.1             |
| Validación           | Pydantic                           | 2.13.4             |
| Tokens               | PyJWT                              | 2.10.1             |
| Cliente HTTP         | httpx                              | 0.28.1             |
| Inteligencia artificial | TensorFlow (CPU) / Keras        | 2.18.0             |
| Procesamiento de audio | librosa / ffmpeg / libsndfile    | 0.10.2.post1       |
| Imágenes             | Pillow                             | 11.0.0             |
| Base de datos        | SQLite                             | 3 (incluida en Python) |
| Lenguaje frontend    | TypeScript                         | 6.0                |
| Framework UI         | React                              | 19.2               |
| Componentes UI       | Material UI (MUI)                  | 9.3                |
| Enrutamiento         | React Router                       | 7.18               |
| Empaquetador         | Vite                               | 8.2                |
| Servidor web / proxy | Nginx                              | 1.27 (alpine)      |
| Contenedores         | Docker y Docker Compose            | Compose v2         |
| Certificados TLS     | Let's Encrypt (certbot)            | —                  |
| Infraestructura      | Amazon EC2 (Debian), DuckDNS       | —                  |

### 2.4 Estructura del repositorio

```
pg-analisisdesonidos/
├── docker-compose.yml      Orquestación de los tres contenedores
├── reverse/
│   └── nginx.conf          Configuración del proxy inverso (HTTPS)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example        Plantilla de variables de entorno
│   ├── main.py             Punto de entrada de FastAPI
│   ├── database.py         Motor SQLAlchemy y sesión
│   ├── seed.py             Carga del catálogo inicial
│   ├── alembic.ini
│   ├── alembic/            Migraciones de la base de datos
│   ├── routers/            Controladores HTTP (endpoints)
│   ├── services/           Lógica de negocio e inferencia del CNN
│   ├── crud/               Acceso a datos
│   ├── models/             Entidades SQLAlchemy (tablas)
│   ├── schemas/            DTO de entrada y salida (Pydantic)
│   ├── middleware/         CORS y registro de tiempos
│   ├── utils/              JWT, dependencia de usuario actual y del CNN
│   ├── modelos/            Modelo entrenado (.keras) y su configuración
│   └── data/               Base SQLite y PNG de espectrogramas (no versionado)
├── frontend/
│   ├── Dockerfile          Build con Node y servido con Nginx
│   ├── nginx.conf          Configuración de la SPA
│   ├── package.json
│   └── src/
│       ├── main.tsx, App.tsx   Arranque y rutas
│       ├── config.ts           URL base de la API
│       ├── api/                Cliente HTTP y llamadas a la API
│       ├── auth/               Contexto de autenticación
│       ├── components/         Layout y ruta protegida
│       ├── pages/              Pantallas
│       └── types.ts            Tipos compartidos
├── archivoscnn/            Material de referencia de la integración del CNN
├── dercas/                 Especificación de requerimientos
└── manuales/               Manual de usuario y manual técnico
```

<div style="page-break-after: always;"></div>

## 3. Backend

### 3.1 Organización en capas

El backend sigue una arquitectura en capas. Cada capa solo conoce a la inmediatamente inferior:

| Capa        | Carpeta     | Responsabilidad                                                                                 |
|-------------|-------------|-------------------------------------------------------------------------------------------------|
| Routers     | `routers/`  | Definen los endpoints, reciben y validan la petición, inyectan dependencias y devuelven la respuesta. |
| Services    | `services/` | Reglas de negocio. No conocen HTTP: lanzan excepciones de dominio (`NotFoundError`, `ConflictError`). |
| CRUD        | `crud/`     | Consultas a la base de datos con SQLAlchemy.                                                    |
| Models      | `models/`   | Entidades SQLAlchemy mapeadas a tablas.                                                         |
| Schemas     | `schemas/`  | DTO de Pydantic: validan la entrada y definen la forma de la salida.                            |

Las dependencias se resuelven con el sistema de inyección de FastAPI (`Depends`):

- `get_db` (`database.py`): abre una sesión de base de datos por petición y la cierra al terminar.
- `get_current_user` (`utils/auth.py`): valida el JWT y devuelve el usuario autenticado.
- `get_cnn_service` (`utils/cnn.py`): entrega la instancia única del servicio del CNN.

### 3.2 Punto de entrada y ciclo de vida

`main.py` crea la aplicación con `root_path="/api"`, de modo que la documentación interactiva y las URL generadas consideren el prefijo que agrega el proxy.

Durante el arranque (`lifespan`), el backend carga una sola vez el modelo CNN desde `MODELO_CNN_PATH` y `MODELO_CNN_CONFIG` y lo guarda en `app.state.cnn_service`. Si la carga falla, la aplicación sigue en funcionamiento, registra el error y el endpoint de análisis responde `503`.

La documentación interactiva de la API (Swagger UI) está disponible en `https://<TU_DOMINIO>/api/docs`.

### 3.3 Middleware y manejo de errores

`middleware/__init__.py` registra:

- **CORS**, con los orígenes de `CORS_ORIGINS`.
- **Registro de tiempos**: cada petición se escribe en el log con método, ruta, código de estado y duración, y la respuesta incluye el encabezado `X-Process-Time-ms`.

Las excepciones de dominio se traducen a códigos HTTP en `main.py`:

| Excepción        | Código HTTP | Uso                                                  |
|------------------|-------------|------------------------------------------------------|
| `NotFoundError`  | 404         | La entidad solicitada no existe.                     |
| `ConflictError`  | 409         | Se viola una restricción de unicidad.                |

Todas las respuestas de error tienen la forma `{"detail": "<mensaje>"}`.

### 3.4 Catálogo de endpoints

Las rutas se muestran sin el prefijo `/api`. La columna *Auth* indica si se requiere el encabezado `Authorization: Bearer <JWT>`.

**Autenticación** (`routers/auth.py`)

| Método | Ruta                     | Auth | Descripción                                                        |
|--------|--------------------------|------|--------------------------------------------------------------------|
| GET    | `/auth/google/login`     | No   | Redirige a la pantalla de consentimiento de Google.                |
| GET    | `/auth/google/callback`  | No   | Recibe el código de Google, registra al usuario y emite el JWT.    |
| GET    | `/auth/github/login`     | No   | Redirige a la autorización de GitHub.                              |
| GET    | `/auth/github/callback`  | No   | Recibe el código de GitHub, registra al usuario y emite el JWT.    |

**Usuarios** (`routers/usuario.py`)

| Método | Ruta                     | Auth | Descripción                                        |
|--------|--------------------------|------|----------------------------------------------------|
| GET    | `/usuarios/me`           | Sí   | Devuelve el usuario autenticado.                   |
| GET    | `/usuarios`              | No   | Lista usuarios (paginado con `skip` y `limit`).    |
| GET    | `/usuarios/{id_usuario}` | No   | Obtiene un usuario por id.                         |
| POST   | `/usuarios/login-oauth`  | No   | Crea o actualiza un usuario a partir de una identidad OAuth. |

**Catálogo** (`routers/marca.py`, `routers/modelo.py`)

| Método | Ruta                    | Auth | Descripción                                                   |
|--------|-------------------------|------|---------------------------------------------------------------|
| GET    | `/marcas`               | No   | Lista las marcas.                                             |
| GET    | `/marcas/{id_marca}`    | No   | Obtiene una marca.                                            |
| POST   | `/marcas`               | No   | Crea una marca.                                               |
| GET    | `/modelos`              | No   | Lista los modelos. Con `?id_marca=` filtra por marca.         |
| GET    | `/modelos/{id_modelo}`  | No   | Obtiene un modelo.                                            |
| POST   | `/modelos`              | No   | Crea un modelo.                                               |

**Modelos CNN** (`routers/modelo_cnn.py`)

| Método | Ruta                                  | Auth | Descripción                                          |
|--------|---------------------------------------|------|------------------------------------------------------|
| GET    | `/modelos-cnn`                        | No   | Lista las versiones registradas del CNN.             |
| GET    | `/modelos-cnn/activo`                 | No   | Devuelve la versión activa.                          |
| GET    | `/modelos-cnn/{id_modelo_cnn}`        | No   | Obtiene una versión.                                 |
| POST   | `/modelos-cnn`                        | No   | Registra una versión.                                |
| PATCH  | `/modelos-cnn/{id_modelo_cnn}/activar`| No   | Activa una versión y desactiva la anterior.          |

**Diagnósticos** (`routers/diagnostico.py`)

| Método | Ruta                              | Auth | Descripción                                                               |
|--------|-----------------------------------|------|---------------------------------------------------------------------------|
| POST   | `/diagnosticos/analizar`          | Sí   | Analiza un audio y guarda el diagnóstico.                                 |
| GET    | `/diagnosticos/mis`               | Sí   | Historial del usuario autenticado, del más reciente al más antiguo.       |
| GET    | `/diagnosticos/{id_diagnostico}`  | Sí   | Detalle de un diagnóstico. Responde `403` si pertenece a otro usuario.    |

**Otros** (`main.py`)

| Método | Ruta              | Auth | Descripción                                                     |
|--------|-------------------|------|-----------------------------------------------------------------|
| GET    | `/media/{ruta}`   | No   | Sirve las imágenes PNG de los espectrogramas.                   |
| GET    | `/`               | No   | Comprobación de que el backend responde.                        |

**Detalle de `POST /diagnosticos/analizar`**

Cuerpo `multipart/form-data`:

| Campo         | Tipo    | Obligatorio | Validación                                         |
|---------------|---------|-------------|----------------------------------------------------|
| `audio`       | archivo | Sí          | Extensión `wav`, `mp3`, `m4a`, `ogg` o `webm`; máximo 20 MB; no vacío. |
| `id_modelo`   | entero  | Sí          | Debe existir en la tabla `modelo`.                 |
| `anio`        | entero  | Sí          | Entre 1980 y 2100.                                 |
| `kilometraje` | entero  | No          | Mayor o igual a 0.                                 |
| `notas`       | texto   | No          | —                                                  |

El cilindraje que recibe el modelo se toma del modelo de moto en la base de datos, nunca del cliente.

Respuestas de error:

| Código | Causa                                                                   |
|--------|-------------------------------------------------------------------------|
| 400    | Formato no soportado, archivo vacío o mayor de 20 MB.                   |
| 401    | Token ausente, inválido o expirado.                                     |
| 404    | El `id_modelo` no existe.                                               |
| 422    | ffmpeg o librosa no pudieron procesar el audio.                         |
| 503    | El modelo CNN no se cargó o no hay ninguna versión activa en la BD.     |

### 3.5 Almacenamiento de espectrogramas

Cada análisis genera un PNG en `ESPECTROGRAMAS_DIR` (por defecto `data/espectrogramas/`) con un nombre UUID aleatorio. En la base de datos se guarda la ruta relativa (`espectrogramas/<uuid>.png`) en la columna `espectrograma_ref`, y el frontend la muestra mediante `GET /media/<espectrograma_ref>`.

El endpoint `/media` valida que la ruta resuelta quede dentro de `MEDIA_DIR`, lo que impide el acceso a otros archivos del servidor (*path traversal*).

<div style="page-break-after: always;"></div>

## 4. Autenticación y autorización

### 4.1 Flujo OAuth 2.0

MotorScan no almacena contraseñas. Delega la autenticación a Google o GitHub mediante el flujo *Authorization Code* de OAuth 2.0:

```
Navegador            Frontend             Backend                    Google / GitHub
   │  Clic "Continuar   │                     │                              │
   │  con Google"       │                     │                              │
   │──────────────────► │ GET /api/auth/google/login                         │
   │                    │───────────────────► │ Genera "state" y lo guarda   │
   │                    │                     │ en cookie httpOnly           │
   │ ◄──────────────────────── 302 ───────────│                              │
   │ ─────────────────────── Consentimiento ──────────────────────────────►  │
   │ ◄──────────── 302 a GOOGLE_CALLBACK_URL?code=...&state=... ──────────── │
   │ ──────────────────────────────────────► │ Valida state (anti-CSRF)     │
   │                    │                     │ Intercambia code por token ─►│
   │                    │                     │ Obtiene perfil (email, sub) ►│
   │                    │                     │ Crea/actualiza el usuario    │
   │                    │                     │ Firma un JWT propio          │
   │ ◄──── 302 a FRONTEND_URL/auth/callback?token=<JWT> ──                   │
   │──────────────────► │ Guarda el JWT en localStorage y abre la app        │
```

Puntos clave:

- El parámetro `state` se guarda en la cookie `oauth_state` (httpOnly, 10 minutos) y se compara al volver; si no coincide, se responde `400` para prevenir ataques CSRF.
- Con Google se exige `email_verified = true`. Se usa el claim `sub` como identificador estable del usuario.
- Con GitHub, si el email del perfil es privado, se consulta `/user/emails` y se toma el principal.
- Los tokens de Google y GitHub solo se usan durante el callback y no se almacenan.

> **PRECAUCIÓN:** la URL de callback registrada en la consola de cada proveedor debe coincidir exactamente con `GOOGLE_CALLBACK_URL` y `GITHUB_CALLBACK_URL`. Google exige además HTTPS y un nombre de dominio; no admite direcciones IP ni `http`, salvo `localhost`.

### 4.2 Token JWT

Tras el login, el backend emite su propio JWT (`utils/security.py`):

| Característica | Valor                                                          |
|----------------|----------------------------------------------------------------|
| Algoritmo      | `JWT_ALGORITHM` (por defecto HS256)                            |
| Clave          | `SECRET_KEY`                                                   |
| Claims         | `sub` (id del usuario) y `exp` (expiración)                    |
| Vigencia       | `ACCESS_TOKEN_EXPIRE_MINUTES` (por defecto 60 minutos)         |
| Transporte     | Encabezado `Authorization: Bearer <token>`                     |

`get_current_user` verifica la firma y la expiración, y comprueba que el usuario siga existiendo. Cualquier fallo responde `401`. No existe *refresh token*: al expirar el JWT, el frontend descarta la sesión y el usuario debe iniciar sesión de nuevo.

> **PRECAUCIÓN:** cambiar `SECRET_KEY` invalida todas las sesiones activas.

### 4.3 Registro y vinculación de usuarios

`services/usuario.login_oauth` realiza un *upsert* idempotente:

1. Busca al usuario por el par (`proveedor_oauth`, `id_externo_proveedor`).
2. Si no lo encuentra, lo busca por email. Así, una persona que entró con GitHub y luego entra con Google con el mismo email reutiliza su cuenta.
3. Si no existe, lo crea. Si existe, actualiza email, nombre y `ultimo_acceso`.

La autorización sobre los datos es por propietario: un usuario solo puede consultar sus propios diagnósticos.

<div style="page-break-after: always;"></div>

## 5. Módulo de inteligencia artificial

### 5.1 Modelo CNN

El modelo es una red neuronal convolucional de Keras con **dos entradas**:

| Entrada        | Forma            | Contenido                                                  |
|----------------|------------------|------------------------------------------------------------|
| Espectrograma  | (1, 128, 173, 1) | Espectrograma de Mel normalizado en el rango [0, 1].        |
| Cilindraje     | (1, 1)           | Cilindraje normalizado: `(cilindraje − 125) / 75`.         |

La salida es una neurona con activación sigmoide (valor entre 0 y 1).

Archivos, en `backend/modelos/` (montada como volumen en el contenedor):

| Archivo                | Descripción                                           |
|------------------------|-------------------------------------------------------|
| `modelo_cnn_v1.keras`  | Arquitectura y pesos entrenados.                      |
| `model_config.json`    | Parámetros de preprocesamiento, clases e interpretación de la salida. |

> **NOTA:** la versión actual (`v1.0-sintetico`) fue entrenada con datos sintéticos para validar el flujo de extremo a extremo. Su exactitud de validación no es representativa del desempeño con grabaciones reales y debe reentrenarse con un conjunto de datos real.

### 5.2 Archivo de configuración del modelo

`model_config.json` es el contrato entre el entrenamiento y la inferencia. El servicio lee de él todos los parámetros, por lo que **deben ser idénticos a los usados al entrenar**.

| Clave                                    | Valor actual                   |
|------------------------------------------|--------------------------------|
| `version`                                | `v1.0-sintetico`               |
| `clases`                                 | `normal`, `anomalia`           |
| `input_espectrograma.shape`              | `[128, 173, 1]`                |
| `input_cilindraje.normalizacion`         | `(cilindraje - 125) / 75`      |
| `preprocesamiento_audio.sample_rate`     | 22050 Hz                       |
| `preprocesamiento_audio.n_fft`           | 2048                           |
| `preprocesamiento_audio.hop_length`      | 512                            |
| `preprocesamiento_audio.n_mels`          | 128                            |
| `preprocesamiento_audio.fmin` / `fmax`   | 20 Hz / 8000 Hz                |
| `preprocesamiento_audio.duration_seconds`| 4.0                            |
| `preprocesamiento_audio.normalize_db`    | `true`                         |
| `salida.interpretacion`                  | `>= 0.5` anomalía, `< 0.5` normal |

### 5.3 Preprocesamiento del audio

Implementado en `services/cnn_service.py`, método `_audio_a_espectrograma`:

1. **Transcodificación.** ffmpeg convierte cualquier formato de entrada a WAV PCM mono de 44,1 kHz. Es necesario porque libsndfile no lee contenedores como WebM, que es el formato que genera `MediaRecorder` en la mayoría de navegadores.
2. **Carga.** librosa remuestrea a 22 050 Hz y lee como máximo 4 segundos.
3. **Ajuste de duración.** Si el audio dura menos de 4 s, se rellena con ceros; si dura más, se recorta.
4. **Espectrograma de Mel** con `n_fft`, `hop_length`, `n_mels`, `fmin` y `fmax` del archivo de configuración.
5. **Escala logarítmica** (`power_to_db` con referencia al máximo).
6. **Normalización min-max** al rango [0, 1].
7. **Ajuste del eje temporal** a 173 columnas.

La imagen PNG que se guarda se genera con el mismo método, por lo que es idéntica a la entrada del modelo. Se colorea con una paleta tipo *magma*, se invierte verticalmente para que las frecuencias bajas queden abajo y se escala a 256 px de alto con Pillow.

### 5.4 Inferencia y cálculo de la confianza

```
valor     = modelo.predict([espectrograma, cilindraje_normalizado])   # 0..1
clase     = "anomalia" si valor >= 0.5, si no "normal"
confianza = min(|valor − 0.5| × 200, 100)                              # 0..100 %
```

La confianza expresa la distancia del valor al umbral de decisión: 0 % significa que el valor quedó justo en 0,5, y 100 % que quedó en 0 o en 1.

### 5.5 Reemplazo del modelo

Para desplegar un modelo reentrenado:

1. Copie el nuevo `.keras` y su `model_config.json` a `backend/modelos/` en el servidor. Si cambia el nombre del archivo, defina `MODELO_CNN_PATH` en `backend/.env`.
2. Verifique que el preprocesamiento del entrenamiento coincide con el `model_config.json`.
3. Registre la versión en la base de datos y actívela:
   ```bash
   curl -X POST https://<TU_DOMINIO>/api/modelos-cnn \
     -H "Content-Type: application/json" \
     -d '{"version":"v2.0","fecha_entrenamiento":"2026-11-01T00:00:00","exactitud_validacion":92.5,"archivo_pesos":"modelo_cnn_v2.keras","descripcion":"Entrenado con datos reales","activo":1}'
   ```
4. Reinicie el backend para que cargue el nuevo modelo:
   ```bash
   docker compose restart backend
   docker compose logs backend | grep "Modelo CNN cargado"
   ```

Cada diagnóstico guarda el `id_modelo_cnn` activo en el momento del análisis, lo que permite saber qué versión generó cada resultado.

<div style="page-break-after: always;"></div>

## 6. Base de datos

### 6.1 Motor y conexión

Se utiliza **SQLite**, en el archivo indicado por `DATABASE_URL` (en producción, `/app/data/sonidos_motos.db`, que corresponde a `backend/data/sonidos_motos.db` en el host).

`database.py` activa `PRAGMA foreign_keys=ON` en cada conexión, porque SQLite no aplica las llaves foráneas por defecto.

### 6.2 Modelo de datos

```
marca 1───* modelo 1───* diagnostico *───1 usuario
                              *
                              │
                              1
                          modelo_cnn
```

**Tabla `usuario`**

| Columna                | Tipo     | Restricciones                                         |
|------------------------|----------|-------------------------------------------------------|
| `id_usuario`           | INTEGER  | PK, autoincremental                                   |
| `proveedor_oauth`      | TEXT     | NOT NULL, `IN ('google', 'github')`                   |
| `id_externo_proveedor` | TEXT     | NOT NULL; UNIQUE junto con `proveedor_oauth`          |
| `email`                | TEXT     | NOT NULL, UNIQUE                                      |
| `nombre`               | TEXT     | NULL                                                  |
| `fecha_registro`       | DATETIME | NOT NULL, por defecto la fecha actual                 |
| `ultimo_acceso`        | DATETIME | NULL                                                  |

**Tabla `marca`**

| Columna    | Tipo    | Restricciones          |
|------------|---------|------------------------|
| `id_marca` | INTEGER | PK, autoincremental    |
| `nombre`   | TEXT    | NOT NULL, UNIQUE       |

**Tabla `modelo`**

| Columna      | Tipo    | Restricciones                                                   |
|--------------|---------|-----------------------------------------------------------------|
| `id_modelo`  | INTEGER | PK, autoincremental                                             |
| `id_marca`   | INTEGER | FK → `marca`, ON DELETE RESTRICT                                |
| `nombre`     | TEXT    | NOT NULL; UNIQUE junto con `id_marca`                           |
| `cilindraje` | INTEGER | NOT NULL, `IN (125, 150, 155, 160, 180, 190, 200)`              |

**Tabla `modelo_cnn`**

| Columna                | Tipo     | Restricciones                                                   |
|------------------------|----------|-----------------------------------------------------------------|
| `id_modelo_cnn`        | INTEGER  | PK, autoincremental                                             |
| `version`              | TEXT     | NOT NULL, UNIQUE                                                |
| `fecha_entrenamiento`  | DATETIME | NOT NULL                                                        |
| `exactitud_validacion` | REAL     | NOT NULL, entre 0 y 100                                         |
| `archivo_pesos`        | TEXT     | NOT NULL                                                        |
| `descripcion`          | TEXT     | NULL                                                            |
| `activo`               | INTEGER  | NOT NULL, 0 o 1; índice único parcial: solo una fila con `activo = 1` |

**Tabla `diagnostico`**

| Columna             | Tipo     | Restricciones                                        |
|---------------------|----------|------------------------------------------------------|
| `id_diagnostico`    | INTEGER  | PK, autoincremental                                  |
| `id_usuario`        | INTEGER  | FK → `usuario`, ON DELETE CASCADE                    |
| `id_modelo`         | INTEGER  | FK → `modelo`, ON DELETE RESTRICT                    |
| `id_modelo_cnn`     | INTEGER  | FK → `modelo_cnn`, ON DELETE RESTRICT                |
| `anio`              | INTEGER  | NOT NULL, entre 1980 y 2100                          |
| `kilometraje`       | INTEGER  | NULL o mayor o igual a 0                             |
| `notas`             | TEXT     | NULL                                                 |
| `espectrograma_ref` | TEXT     | NOT NULL; ruta relativa del PNG                      |
| `resultado`         | TEXT     | NOT NULL, `IN ('normal', 'anomalia')`                |
| `confianza`         | REAL     | NOT NULL, entre 0 y 100                              |
| `fecha_diagnostico` | DATETIME | NOT NULL, por defecto la fecha actual                |

Índices: `idx_diagnostico_usuario_fecha` (`id_usuario`, `fecha_diagnostico DESC`), que optimiza el historial; `idx_diagnostico_modelo`; `idx_diagnostico_modelo_cnn`; `idx_modelo_marca`.

### 6.3 Migraciones

El esquema se administra con Alembic (`backend/alembic/versions/`). El backend **no** crea las tablas al arrancar; deben aplicarse las migraciones.

| Revisión       | Descripción                                                        |
|----------------|--------------------------------------------------------------------|
| `13c6d5cbb9f2` | Esquema inicial de las cinco tablas.                               |
| `a1b2c3d4e5f6` | Renombra `audio_ref` a `espectrograma_ref` en `diagnostico`.       |
| `b2c3d4e5f6a7` | Amplía los valores permitidos de `cilindraje` en `modelo`.         |

`alembic/env.py` usa `DATABASE_URL` si está definida; si no, usa el valor de `alembic.ini`.

Comandos frecuentes (en producción, dentro del contenedor):

```bash
docker compose exec backend alembic upgrade head      # aplicar migraciones pendientes
docker compose exec backend alembic current           # ver la revisión actual
docker compose exec backend alembic history           # ver el historial
```

Para crear una migración después de modificar un modelo (en desarrollo):

```bash
cd backend
alembic revision --autogenerate -m "descripcion del cambio"
```

> **NOTA:** SQLite no admite la mayoría de las sentencias `ALTER TABLE`. Para cambiar columnas o restricciones, use `op.batch_alter_table`, como en las migraciones existentes.

### 6.4 Datos iniciales (seed)

`seed.py` carga el catálogo de referencia y es idempotente (se puede ejecutar varias veces sin duplicar registros):

- 11 marcas: Honda, Yamaha, Suzuki, Bajaj, TVS, Hero, Italika, Haojue, Keeway, Kymco y AKT.
- Modelos de 125 a 200 cc de uso común en Guatemala, con su cilindraje.
- Un registro de `modelo_cnn` activo (`v1.0`), si no existe ninguno.

```bash
docker compose exec backend python seed.py
```

Para agregar marcas o modelos, edite las listas `MARCAS` y `MODELOS` y vuelva a ejecutar el script.

<div style="page-break-after: always;"></div>

## 7. Frontend

### 7.1 Estructura

El frontend es una *Single Page Application* (SPA) en React con TypeScript, diseñada con prioridad para el móvil y construida con componentes de Material UI.

| Carpeta / archivo          | Contenido                                                            |
|----------------------------|----------------------------------------------------------------------|
| `src/main.tsx`             | Monta la aplicación con el tema, el router y el `AuthProvider`.      |
| `src/App.tsx`              | Definición de rutas.                                                 |
| `src/config.ts`            | `API_URL`: `VITE_API_URL` o `/api` por defecto.                      |
| `src/theme.ts`             | Tema de Material UI.                                                 |
| `src/api/`                 | `client.ts` (wrapper de `fetch`), `catalogo.ts`, `diagnostico.ts`.   |
| `src/auth/AuthContext.tsx` | Estado de la sesión y funciones de login y logout.                   |
| `src/components/`          | `AppLayout` (navegación inferior), `ProtectedRoute`, `MobileShell`.  |
| `src/pages/`               | Pantallas de la aplicación.                                          |
| `src/pages/diagnostico/`   | Asistente de diagnóstico: `PasoDatosMoto`, `PasoAudio`, `PasoResultado`. |
| `src/types.ts`             | Tipos que reflejan los DTO del backend.                              |

En producción, el `Dockerfile` compila la aplicación con Node 22 (`npm ci` y `npm run build`) y sirve la carpeta `dist` con Nginx. `frontend/nginx.conf` redirige cualquier ruta desconocida a `index.html` para que funcione el enrutamiento del lado del cliente, y aplica caché de un año a `/assets/`, cuyos nombres incluyen un hash.

### 7.2 Rutas

| Ruta                   | Pantalla                  | Protegida |
|------------------------|---------------------------|-----------|
| `/login`               | Inicio de sesión          | No        |
| `/auth/callback`       | Recepción del JWT         | No        |
| `/`                    | Inicio                    | Sí        |
| `/historial`           | Historial de diagnósticos | Sí        |
| `/perfil`              | Perfil del usuario        | Sí        |
| `/diagnostico/nuevo`   | Asistente de diagnóstico  | Sí        |
| `/diagnostico/:id`     | Detalle de diagnóstico    | Sí        |
| `/acerca-de`           | Información del sistema   | Sí        |
| Cualquier otra         | Redirige a `/`            | —         |

`ProtectedRoute` muestra un indicador de carga mientras se valida la sesión y redirige a `/login` si no hay usuario.

### 7.3 Gestión de la sesión

- El JWT se guarda en `localStorage` con la clave `motorscan_token`.
- Al cargar la aplicación, `AuthContext` valida el token con `GET /usuarios/me`. Si la respuesta falla (token expirado o inválido), lo elimina y el usuario vuelve al login.
- `loginConGoogle` y `loginConGithub` redirigen el navegador a `/api/auth/<proveedor>/login`.
- `logout` elimina el token del navegador. No hay invalidación en el servidor: el token deja de ser válido cuando expira.

### 7.4 Comunicación con la API

`api/client.ts` expone `apiFetch`, que agrega la URL base, el encabezado JSON y el `Bearer` token, y convierte las respuestas de error en `ApiError` con el código de estado y el `detail` del backend.

`analizarAudio` (`api/diagnostico.ts`) envía un `FormData` y no fija `Content-Type`, para que el navegador agregue el *boundary* del multipart. La grabación se realiza con la API `MediaRecorder` del navegador; el formato resultante (normalmente WebM u Ogg) lo convierte ffmpeg en el backend.

<div style="page-break-after: always;"></div>

## 8. Configuración

### 8.1 Variables de entorno del backend

Se definen en `backend/.env`, que Docker Compose carga mediante `env_file`. La plantilla es `backend/.env.example`.

> **PRECAUCIÓN:** `backend/.env` contiene secretos y está excluido del repositorio por `.gitignore`. Debe crearse manualmente en cada servidor y nunca debe subirse a Git.

| Variable                      | Obligatoria | Valor por defecto                               | Descripción                                                  |
|-------------------------------|-------------|-------------------------------------------------|--------------------------------------------------------------|
| `DATABASE_URL`                | Sí          | `sqlite:///./sonidos_motos.db`                  | Cadena de conexión. En Docker: `sqlite:////app/data/sonidos_motos.db`. |
| `SECRET_KEY`                  | Sí          | Valor inseguro de ejemplo                       | Clave de firma del JWT. Debe ser aleatoria y larga.          |
| `JWT_ALGORITHM`               | No          | `HS256`                                         | Algoritmo de firma.                                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No          | `60`                                            | Vigencia del JWT en minutos.                                 |
| `CORS_ORIGINS`                | Sí          | `http://localhost,http://localhost:5173`        | Orígenes permitidos, separados por coma.                     |
| `FRONTEND_URL`                | Sí          | `http://localhost`                              | URL a la que el backend redirige tras el login.              |
| `GOOGLE_CLIENT_ID`            | Sí*         | —                                               | ID de cliente OAuth de Google.                               |
| `GOOGLE_CLIENT_SECRET`        | Sí*         | —                                               | Secreto de cliente OAuth de Google.                          |
| `GOOGLE_CALLBACK_URL`         | Sí*         | `http://localhost/api/auth/google/callback`     | URL de retorno registrada en Google.                         |
| `GITHUB_CLIENT_ID`            | Sí*         | —                                               | ID de la OAuth App de GitHub.                                |
| `GITHUB_CLIENT_SECRET`        | Sí*         | —                                               | Secreto de la OAuth App de GitHub.                           |
| `GITHUB_CALLBACK_URL`         | Sí*         | `http://localhost/api/auth/github/callback`     | URL de retorno registrada en GitHub.                         |
| `MODELO_CNN_PATH`             | No          | `modelos/modelo_cnn_v1.keras`                   | Ruta del modelo Keras.                                       |
| `MODELO_CNN_CONFIG`           | No          | `modelos/model_config.json`                     | Ruta de la configuración del modelo.                         |
| `MEDIA_DIR`                   | No          | `data`                                          | Carpeta raíz que sirve `/media`.                             |
| `ESPECTROGRAMAS_DIR`          | No          | `data/espectrogramas`                           | Carpeta donde se guardan los PNG.                            |

\* Obligatoria para el proveedor que se quiera habilitar.

Para generar `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Ejemplo de producción:

```env
DATABASE_URL=sqlite:////app/data/sonidos_motos.db
SECRET_KEY=<valor generado>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://<TU_DOMINIO>
FRONTEND_URL=https://<TU_DOMINIO>
GOOGLE_CLIENT_ID=<id>
GOOGLE_CLIENT_SECRET=<secreto>
GOOGLE_CALLBACK_URL=https://<TU_DOMINIO>/api/auth/google/callback
GITHUB_CLIENT_ID=<id>
GITHUB_CLIENT_SECRET=<secreto>
GITHUB_CALLBACK_URL=https://<TU_DOMINIO>/api/auth/github/callback
```

Después de modificar `.env`, recree el contenedor para que lea los valores nuevos:

```bash
docker compose up -d --force-recreate backend
```

### 8.2 Variables de entorno del frontend

| Variable       | Valor por defecto | Descripción                                                                                      |
|----------------|-------------------|--------------------------------------------------------------------------------------------------|
| `VITE_API_URL` | `/api`            | URL base de la API. Solo es necesaria en desarrollo, cuando el backend corre en otro puerto.     |

Las variables `VITE_*` se insertan en el código durante la compilación, no en tiempo de ejecución.

<div style="page-break-after: always;"></div>

## 9. Instalación del entorno de desarrollo

### 9.1 Requisitos

- Git
- Python 3.12
- Node.js 22 y npm
- ffmpeg y libsndfile (`sudo apt install ffmpeg libsndfile1`)

### 9.2 Backend

```bash
git clone https://github.com/rramirezg18/pg-analisisdesonidos.git
cd pg-analisisdesonidos/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Para desarrollo, ajuste `backend/.env` así (el backend se ejecuta directamente con uvicorn, sin el prefijo `/api`):

```env
DATABASE_URL=sqlite:///./sonidos_motos.db
CORS_ORIGINS=http://localhost:5173
FRONTEND_URL=http://localhost:5173
GOOGLE_CALLBACK_URL=http://localhost:8001/auth/google/callback
GITHUB_CALLBACK_URL=http://localhost:8001/auth/github/callback
```

Las URL de callback de desarrollo también deben estar registradas en Google Cloud Console y en una OAuth App de GitHub para desarrollo (GitHub solo admite una URL de callback por aplicación).

El backend no carga el archivo `.env` por sí mismo, así que hay que exportar las variables antes de iniciarlo:

```bash
set -a; source .env; set +a
alembic upgrade head
python seed.py
uvicorn main:app --reload --port 8001
```

La documentación de la API queda disponible en `http://localhost:8001/docs`.

### 9.3 Frontend

En otra terminal:

```bash
cd pg-analisisdesonidos/frontend
npm install
VITE_API_URL=http://localhost:8001 npm run dev
```

La aplicación queda disponible en `http://localhost:5173`.

Otros comandos:

| Comando           | Descripción                                          |
|-------------------|------------------------------------------------------|
| `npm run build`   | Verifica tipos con TypeScript y compila a `dist/`.   |
| `npm run lint`    | Ejecuta ESLint.                                      |
| `npm run preview` | Sirve localmente la versión compilada.               |

> **NOTA:** `reverse/nginx.conf` está configurado para HTTPS y requiere los certificados de Let's Encrypt. Por eso, `docker compose up` no funciona en una máquina de desarrollo sin certificados; use el procedimiento de esta sección.

<div style="page-break-after: always;"></div>

## 10. Despliegue en producción

Esta sección describe el despliegue en un servidor Amazon EC2 con Debian, con el dominio gratuito de DuckDNS y certificado de Let's Encrypt. El dominio de producción actual es `talleraguilasonidos.duckdns.org`.

### 10.1 Requisitos del servidor

| Recurso        | Mínimo recomendado                                                      |
|----------------|-------------------------------------------------------------------------|
| Sistema        | Debian 12 o Ubuntu 22.04 o superior                                     |
| Memoria        | 2 GB de RAM (TensorFlow carga el modelo en memoria)                     |
| Disco          | 10 GB libres (la imagen del backend con TensorFlow ocupa varios GB)     |
| Software       | Git, Docker Engine con el plugin Compose, certbot                       |
| Red            | Puertos 22, 80 y 443 abiertos                                           |

### 10.2 Infraestructura en AWS

1. **IP elástica.** En EC2 → *Red y seguridad* → *Direcciones IP elásticas*, asigne una dirección y asóciela a la instancia. Así la IP pública no cambia al detener e iniciar la instancia.
2. **Grupo de seguridad.** Permita el tráfico entrante en los puertos 22 (SSH, idealmente restringido a su IP), 80 (HTTP) y 443 (HTTPS) desde `0.0.0.0/0`.

> **PRECAUCIÓN:** una IP elástica que no está asociada a una instancia en ejecución genera cobro. Libérela si elimina la instancia.

### 10.3 Dominio (DuckDNS)

1. Inicie sesión en https://www.duckdns.org.
2. Cree el subdominio y escriba la IP elástica en *current ip*.
3. Verifique desde el servidor:
   ```bash
   getent hosts <TU_DOMINIO>
   ```

### 10.4 Instalación de Docker

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER     # cierre y vuelva a abrir la sesión SSH
```

En Ubuntu, sustituya `debian` por `ubuntu` en las dos URL.

### 10.5 Obtención del código y configuración

```bash
cd ~
git clone https://github.com/rramirezg18/pg-analisisdesonidos.git
cd pg-analisisdesonidos
cp backend/.env.example backend/.env
nano backend/.env
```

Complete el archivo según el ejemplo de producción de la sección 8.1.

### 10.6 Certificado HTTPS

El certificado se obtiene con certbot en modo *standalone*, que levanta un servidor temporal en el puerto 80. Por eso el proxy debe estar detenido durante la emisión:

```bash
sudo apt install -y certbot
docker compose stop proxy          # solo si ya estaba en ejecución

sudo certbot certonly --standalone \
  -d <TU_DOMINIO> \
  -m <CORREO> --agree-tos -n \
  --pre-hook "docker compose -f /home/admin/pg-analisisdesonidos/docker-compose.yml stop proxy" \
  --post-hook "docker compose -f /home/admin/pg-analisisdesonidos/docker-compose.yml start proxy"
```

Los certificados quedan en `/etc/letsencrypt/live/<TU_DOMINIO>/` y se montan en el contenedor `proxy` como solo lectura. Los *hooks* quedan guardados en la configuración de renovación, de modo que cada renovación automática detiene y vuelve a iniciar el proxy.

Si el dominio cambia, actualice `server_name`, `ssl_certificate` y `ssl_certificate_key` en `reverse/nginx.conf`.

### 10.7 Construcción y arranque

```bash
docker compose up -d --build
docker compose ps
```

Los tres contenedores deben aparecer en estado `Up`. La primera construcción del backend tarda varios minutos por la instalación de TensorFlow.

### 10.8 Inicialización de la base de datos

Solo la primera vez:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python seed.py
```

### 10.9 Configuración de los proveedores OAuth

**Google Cloud Console** → *APIs y servicios* → *Credenciales* → ID de cliente de OAuth 2.0:

| Campo                                   | Valor                                               |
|-----------------------------------------|-----------------------------------------------------|
| Orígenes autorizados de JavaScript      | `https://<TU_DOMINIO>`                              |
| URI de redireccionamiento autorizados   | `https://<TU_DOMINIO>/api/auth/google/callback`     |

Si la pantalla de consentimiento está en estado *Prueba*, solo pueden iniciar sesión los correos registrados como *Usuarios de prueba*. Para permitir el acceso a cualquier cuenta, publique la aplicación.

**GitHub** → *Settings* → *Developer settings* → *OAuth Apps*:

| Campo                       | Valor                                               |
|-----------------------------|-----------------------------------------------------|
| Homepage URL                | `https://<TU_DOMINIO>`                              |
| Authorization callback URL  | `https://<TU_DOMINIO>/api/auth/github/callback`     |

Los cambios en Google pueden tardar desde unos minutos hasta algunas horas en aplicarse.

### 10.10 Verificación

| Prueba                                              | Resultado esperado                               |
|-----------------------------------------------------|--------------------------------------------------|
| Abrir `http://<TU_DOMINIO>`                         | Redirige a `https://` con candado válido.        |
| Abrir `https://<TU_DOMINIO>/api/`                   | Respuesta JSON del backend.                      |
| Abrir `https://<TU_DOMINIO>/api/modelos-cnn/activo` | JSON con la versión activa.                      |
| Iniciar sesión con Google y con GitHub              | Se abre la pantalla de inicio.                   |
| Realizar un diagnóstico                             | Se muestra el resultado y el espectrograma.      |
| `docker compose logs backend \| grep "Modelo CNN"`  | "Modelo CNN cargado: v1.0-sintetico ..."         |

<div style="page-break-after: always;"></div>

## 11. Operación y mantenimiento

### 11.1 Actualizar a una nueva versión del código

```bash
cd ~/pg-analisisdesonidos
git pull
docker compose up -d --build
docker compose exec backend alembic upgrade head    # si hay migraciones nuevas
```

> **PRECAUCIÓN:** no edite en el servidor archivos versionados (por ejemplo, `reverse/nginx.conf` o `docker-compose.yml`). Haga los cambios en el repositorio y despliéguelos con `git pull`; de lo contrario, se producirán conflictos.

### 11.2 Registros (logs)

```bash
docker compose logs -f backend          # peticiones, errores e inferencia
docker compose logs -f proxy            # accesos y errores de Nginx
docker compose logs --tail=100 frontend
```

Cada petición al backend se registra con el formato `METODO /ruta -> código (duración ms)`.

### 11.3 Reiniciar y detener servicios

```bash
docker compose restart backend          # reinicia un servicio
docker compose down                     # detiene y elimina los contenedores (los datos persisten)
docker compose up -d                    # vuelve a iniciar todo
```

Los contenedores tienen `restart: unless-stopped`, por lo que se inician solos al reiniciar el servidor.

### 11.4 Respaldo y restauración

Todos los datos persistentes están en `backend/data/` (base de datos y espectrogramas). El archivo `backend/.env` también debe respaldarse por separado, en un lugar seguro.

Respaldo:

```bash
cd ~/pg-analisisdesonidos
docker compose stop backend
tar czf ~/respaldo-motorscan-$(date +%F).tar.gz backend/data
docker compose start backend
```

Restauración:

```bash
docker compose stop backend
tar xzf ~/respaldo-motorscan-<FECHA>.tar.gz
docker compose start backend
```

Se recomienda copiar los respaldos fuera del servidor (por ejemplo, con `scp` o a Amazon S3).

### 11.5 Renovación del certificado

Los certificados de Let's Encrypt duran 90 días. El paquete certbot instala un temporizador de systemd que intenta la renovación dos veces al día y la aplica cuando faltan menos de 30 días.

```bash
sudo certbot certificates                 # fecha de vencimiento
sudo certbot renew --dry-run              # simulación de la renovación
systemctl list-timers | grep certbot      # estado del temporizador
```

### 11.6 Limpieza de espacio en disco

Las reconstrucciones dejan imágenes antiguas de Docker:

```bash
df -h
docker system df
docker image prune -f
```

### 11.7 Cambio de la dirección IP

Si la IP pública cambia (por ejemplo, si no se usa IP elástica), actualice el valor en DuckDNS. No es necesario cambiar ninguna otra configuración.

<div style="page-break-after: always;"></div>

## 12. Seguridad

### 12.1 Controles implementados

| Control                                   | Implementación                                                         |
|-------------------------------------------|------------------------------------------------------------------------|
| Cifrado en tránsito                       | HTTPS con TLS de Let's Encrypt; HTTP redirige con 301 a HTTPS.         |
| Autenticación delegada                    | OAuth 2.0 con Google y GitHub; no se almacenan contraseñas.            |
| Protección CSRF en el login               | Parámetro `state` aleatorio validado contra una cookie httpOnly.       |
| Sesión firmada                            | JWT HS256 con expiración.                                              |
| Autorización por propietario              | Un usuario solo accede a sus diagnósticos (`403` en otro caso).        |
| Validación de entrada                     | Pydantic, restricciones CHECK en la base de datos y validación del audio. |
| Límite de tamaño                          | 25 MB en el proxy y 20 MB en el backend.                               |
| Prevención de *path traversal*            | Validación de la ruta en `/media`.                                     |
| Nombres de archivo no adivinables         | UUID aleatorio para cada espectrograma.                                |
| Privacidad del audio                      | El audio solo se procesa en memoria y no se almacena.                  |
| Gestión de secretos                       | Variables de entorno en `backend/.env`, excluido de Git.               |
| Superficie expuesta mínima                | Solo el proxy publica puertos; backend y frontend son internos.        |

### 12.2 Riesgos conocidos

> **PRECAUCIÓN:** los siguientes endpoints no requieren autenticación y están expuestos públicamente a través del proxy. Se recomienda protegerlos (por ejemplo, con `Depends(get_current_user)` y un rol de administrador) o eliminarlos antes de un uso en producción con usuarios reales.

| Endpoint                                   | Riesgo                                                             |
|--------------------------------------------|--------------------------------------------------------------------|
| `GET /usuarios`, `GET /usuarios/{id}`      | Exponen los correos y nombres de todos los usuarios registrados.   |
| `POST /usuarios/login-oauth`               | Permite crear o modificar usuarios sin pasar por el proveedor OAuth. |
| `POST /marcas`, `POST /modelos`            | Permiten alterar el catálogo.                                      |
| `POST /modelos-cnn`, `PATCH /modelos-cnn/{id}/activar` | Permiten cambiar la versión activa del modelo registrada en la BD. |

Otras consideraciones:

- El JWT se entrega al frontend como parámetro de la URL de `/auth/callback` y se guarda en `localStorage`. Es vulnerable a robo si existiera una falla XSS en el frontend.
- La documentación de Swagger (`/api/docs`) está expuesta públicamente.
- No hay limitación de frecuencia de peticiones (*rate limiting*) en el endpoint de análisis, que es costoso en CPU.

<div style="page-break-after: always;"></div>

## 13. Solución de problemas

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| El navegador muestra `ERR_CONNECTION_REFUSED`. | El contenedor `proxy` está detenido o falló al iniciar. | `docker compose ps`; `docker compose logs proxy`; `docker compose up -d proxy`. |
| El navegador muestra un tiempo de espera agotado. | El puerto 80 o 443 no está abierto en el grupo de seguridad, o el dominio apunta a otra IP. | Revisar las reglas de entrada y `getent hosts <TU_DOMINIO>`. |
| El log del proxy muestra `cannot load certificate`. | El certificado no existe o la ruta en `nginx.conf` no coincide con el dominio. | `sudo ls /etc/letsencrypt/live/`; volver a ejecutar certbot (sección 10.6). |
| certbot falla con `Address already in use`. | El proxy ocupa el puerto 80. | `docker compose stop proxy` y repetir. |
| Google muestra "Acceso bloqueado: error de autorización" / `invalid_request`. | La URL de callback usa `http` o una IP. | Usar dominio con HTTPS (sección 10). |
| Google muestra `redirect_uri_mismatch`. | `GOOGLE_CALLBACK_URL` no coincide con la URI registrada. | Comparar ambos valores carácter por carácter (esquema, dominio, ruta, sin `/` final). |
| Google muestra "acceso denegado" a una cuenta concreta. | La aplicación está en modo *Prueba* y la cuenta no es usuario de prueba. | Agregar el correo en *Usuarios de prueba* o publicar la aplicación. |
| GitHub muestra "The redirect_uri is not associated with this application". | La *Authorization callback URL* no coincide con `GITHUB_CALLBACK_URL`. | Corregir la URL en la OAuth App. |
| Tras el login aparece "State inválido (posible CSRF)". | La cookie `oauth_state` expiró (más de 10 minutos) o el navegador la bloqueó. | Repetir el inicio de sesión desde la pantalla de login. |
| Tras el login se vuelve a la pantalla de login. | `SECRET_KEY` cambió, el token expiró o `FRONTEND_URL` es incorrecta. | Revisar `backend/.env` y recrear el backend. |
| El análisis responde `503` "El modelo CNN no está disponible". | El archivo `.keras` o `model_config.json` no se pudo cargar. | `docker compose logs backend`; verificar `backend/modelos/`. |
| El análisis responde `503` "No hay modelo CNN activo". | No se ejecutó el seed o no hay ninguna versión con `activo = 1`. | `docker compose exec backend python seed.py`. |
| El análisis responde `422`. | Audio corrupto, vacío o en un formato que ffmpeg no puede decodificar. | Probar con otro archivo; revisar el detalle en los logs del backend. |
| Error `no such table` en los logs. | No se aplicaron las migraciones. | `docker compose exec backend alembic upgrade head`. |
| Los cambios en `.env` no se reflejan. | El contenedor conserva las variables anteriores. | `docker compose up -d --force-recreate backend`. |
| La construcción del backend falla por falta de espacio. | Disco lleno por imágenes antiguas. | `docker image prune -f`; ampliar el volumen EBS. |
| El backend se reinicia constantemente o se cierra sin error. | Memoria insuficiente para TensorFlow. | Usar una instancia con más RAM o agregar memoria swap. |

<div style="page-break-after: always;"></div>

## 14. Limitaciones conocidas y trabajo futuro

| Limitación | Detalle | Propuesta |
|------------|---------|-----------|
| Modelo entrenado con datos sintéticos | La versión `v1.0-sintetico` valida el flujo, pero no garantiza resultados fiables con audio real. | Recolectar grabaciones reales etiquetadas y reentrenar. |
| Inconsistencia en el registro del CNN del seed | El seed registra `v1.0` con exactitud 0 y archivo `pendiente.keras`, que no coinciden con `model_config.json`. | Registrar la versión real con sus métricas al reentrenar (sección 5.5). |
| Análisis limitado a 4 segundos | Solo se usan los primeros 4 s del audio. | Analizar varias ventanas y combinar los resultados. |
| Clasificación binaria | No identifica el tipo de falla. | Ampliar el modelo a clasificación multiclase. |
| SQLite | Adecuada para una sola instancia, con concurrencia de escritura limitada. | Migrar a PostgreSQL si se requiere escalar horizontalmente. |
| Endpoints administrativos sin protección | Ver la sección 12.2. | Agregar autenticación y roles. |
| Sin pruebas automatizadas ni CI/CD | El despliegue es manual. | Agregar pruebas con pytest y un flujo de GitHub Actions. |
| Sin `.dockerignore` | Una carpeta `venv` o `node_modules` local se copia al contexto de construcción. | Agregar `.dockerignore` en `backend/` y `frontend/`. |
| Código sin uso en el frontend | `src/utils/melSpectrogram.ts` (cálculo del espectrograma en el navegador) no se utiliza desde que el cálculo se trasladó al backend, y sus parámetros difieren de `model_config.json`. | Eliminarlo o alinearlo con la configuración del modelo. |
| Configuración de desarrollo con Docker | `reverse/nginx.conf` exige certificados, por lo que Compose no funciona en local. | Crear un archivo de Compose separado para desarrollo. |

<div style="page-break-after: always;"></div>

## 15. Glosario

| Término | Definición |
|---------|------------|
| Alembic | Herramienta de migraciones de esquema para SQLAlchemy. |
| CNN (red neuronal convolucional) | Tipo de red neuronal especializada en datos con estructura de cuadrícula, como imágenes o espectrogramas. |
| CORS | *Cross-Origin Resource Sharing*. Mecanismo que permite a un navegador consumir una API servida desde otro origen. |
| CSRF | *Cross-Site Request Forgery*. Ataque que fuerza al navegador de la víctima a realizar una acción no deseada. |
| Docker Compose | Herramienta que define y ejecuta aplicaciones de varios contenedores a partir de un archivo YAML. |
| DTO | *Data Transfer Object*. Objeto que define la forma de los datos de entrada o salida de la API. |
| DuckDNS | Servicio gratuito de DNS dinámico que asigna subdominios de `duckdns.org`. |
| Espectrograma de Mel | Representación del sonido en tiempo y frecuencia, con el eje de frecuencias en la escala Mel, cercana a la percepción humana. |
| ffmpeg | Herramienta de línea de comandos para decodificar y convertir audio y video. |
| IP elástica | Dirección IPv4 pública y estática de AWS que se puede asociar a una instancia EC2. |
| JWT | *JSON Web Token*. Token firmado que contiene la identidad del usuario y su fecha de expiración. |
| Let's Encrypt | Autoridad de certificación gratuita y automatizada. |
| librosa | Biblioteca de Python para el análisis de audio. |
| OAuth 2.0 | Protocolo de autorización que permite a una aplicación obtener la identidad de un usuario a través de un proveedor externo. |
| Proxy inverso | Servidor que recibe las peticiones de los clientes y las reenvía a los servicios internos. |
| Seed | Script que carga datos iniciales en la base de datos. |
| SPA | *Single Page Application*. Aplicación web que carga una sola página y cambia el contenido sin recargarla. |
| Upsert | Operación que inserta un registro si no existe o lo actualiza si ya existe. |

## 16. Soporte y contacto

| Nombre          | Rol           | Correo electrónico       |
|-----------------|---------------|--------------------------|
| Roberto Ramírez | Desarrollador | rramirezg18@miumg.edu.gt |

Al reportar un problema técnico, incluya la versión desplegada (`git log -1 --oneline`), los comandos ejecutados y la salida de `docker compose ps` y `docker compose logs --tail=100 <servicio>`.

<div style="page-break-after: always;"></div>

## Anexo A. Referencia rápida de comandos

| Tarea | Comando |
|-------|---------|
| Ver el estado de los contenedores | `docker compose ps` |
| Construir e iniciar | `docker compose up -d --build` |
| Aplicar migraciones | `docker compose exec backend alembic upgrade head` |
| Cargar el catálogo | `docker compose exec backend python seed.py` |
| Ver los logs del backend | `docker compose logs -f backend` |
| Recargar las variables de entorno | `docker compose up -d --force-recreate backend` |
| Reiniciar el backend | `docker compose restart backend` |
| Detener todo | `docker compose down` |
| Actualizar el código | `git pull && docker compose up -d --build` |
| Respaldar los datos | `tar czf ~/respaldo-$(date +%F).tar.gz backend/data` |
| Ver la vigencia del certificado | `sudo certbot certificates` |
| Probar la renovación | `sudo certbot renew --dry-run` |
| Abrir una consola en el backend | `docker compose exec backend bash` |
| Consultar la base de datos | `docker compose exec backend python -c "import sqlite3; c=sqlite3.connect('/app/data/sonidos_motos.db'); print(c.execute('select count(*) from diagnostico').fetchone())"` |
| Liberar espacio | `docker image prune -f` |

## Anexo B. Correspondencia con ISO/IEC/IEEE 15289

| Elemento de información | Sección del manual |
|-------------------------|--------------------|
| Identificación, estado y control de versiones | Identificación del documento; Historial de revisiones |
| Propósito, alcance y audiencia | 1. Introducción |
| Referencias | 1.5 Documentos de referencia |
| Descripción de la arquitectura del software | 2. Descripción general del sistema |
| Descripción del diseño de componentes | 3. Backend; 5. Módulo de inteligencia artificial; 7. Frontend |
| Descripción de interfaces | 3.4 Catálogo de endpoints; 4. Autenticación y autorización |
| Descripción del diseño de la base de datos | 6. Base de datos |
| Configuración | 8. Configuración |
| Procedimientos de instalación | 9. Instalación del entorno de desarrollo; 10. Despliegue en producción |
| Procedimientos de operación y mantenimiento | 11. Operación y mantenimiento |
| Seguridad | 12. Seguridad |
| Solución de problemas | 13. Solución de problemas |
| Limitaciones y problemas conocidos | 14. Limitaciones conocidas y trabajo futuro |
| Glosario | 15. Glosario |
| Información de contacto | 16. Soporte y contacto |
