# SmartCampus

Microservicio REST para la gestión de aulas y reservas de espacios universitarios, desarrollado para SmartCampus Solutions como parte de la Práctica 1: automatización y despliegue de una aplicación con Git Hooks y GitHub Actions.

**Equipo:** Fer y Giordano.

> Las secciones marcadas como _pendiente_ las irá completando cada miembro del equipo conforme avance su parte.

## Índice

1. [Descripción](#descripción)
2. [Arquitectura](#arquitectura)
3. [Instalación](#instalación)
4. [Ejecución local](#ejecución-local)
5. [Configuración](#configuración)
6. [API](#api)
7. [Reglas de negocio](#reglas-de-negocio)
8. [Tests](#tests)
9. [Git Hooks](#git-hooks)
10. [Docker](#docker)
11. [Docker Compose](#docker-compose)
12. [GitHub Actions](#github-actions)
13. [Flujo de trabajo en Git](#flujo-de-trabajo-en-git)
14. [Evidencias](#evidencias)

## Descripción

SmartCampus permite a una universidad gestionar sus aulas (nombre, edificio, capacidad y equipamiento) y las reservas de esos espacios, evitando reservas imposibles o solapadas.

El objetivo de la práctica no es solo la aplicación, sino el flujo de automatización que la rodea: Git Hooks que validan el código antes de compartirlo, tests automáticos, contenedores Docker y un pipeline de CI/CD con GitHub Actions.

## Arquitectura

Arquitectura por capas, sin vistas (es una API REST):

```
Cliente → Router (FastAPI) → Service (lógica y SQL) → SQLite
```

```
smartcampus/
├── app/
│   ├── __init__.py
│   ├── main.py          # crea la app FastAPI, registra routers y /health
│   ├── config.py        # configuración por variables de entorno
│   ├── sqlite.py        # conexión SQLite y creación de tablas
│   ├── models.py        # esquemas Pydantic y validaciones
│   ├── services.py      # lógica de negocio y consultas SQL
│   ├── routers/
│   │   ├── rooms.py     # endpoints de aulas
│   │   └── bookings.py  # endpoints de reservas
│   └── db/              # fichero SQLite (ignorado por Git)
├── tests/
│   ├── conftest.py      # BD temporal por test y cliente HTTP
│   ├── test_health.py
│   ├── test_services.py # unitarios
│   ├── test_rooms.py    # integración
│   └── test_bookings.py # integración
├── hooks/
│   ├── pre-commit
│   ├── post-commit
│   ├── pre-push
│   └── post-push
├── install-hooks.sh     # instala los hooks y el alias git pushp
├── pytest.ini
├── ruff.toml
├── requirements.txt
└── README.md
```

- **Routers**: reciben la petición HTTP, llaman a los services y traducen las excepciones a códigos HTTP.
- **Services**: contienen las reglas de negocio y el SQL. Se prueban sin pasar por HTTP.
- **Models**: esquemas Pydantic que validan los datos de entrada (capacidad, formato de horas y fechas, orden de horas).
- **Base de datos**: SQLite con el módulo `sqlite3` de la librería estándar, sin ORM. Las claves foráneas están activadas (`PRAGMA foreign_keys = ON`), por lo que al borrar un aula se borran sus reservas.

### Modelo de datos

**Aula (`rooms`)**: `id`, `nombre`, `edificio`, `capacidad`, `equipamiento` (lista guardada como JSON).

**Reserva (`bookings`)**: `id`, `aula_id` (referencia a `rooms.id`), `usuario`, `fecha` (`YYYY-MM-DD`), `hora_inicio` y `hora_fin` (`HH:MM`).

## Instalación

Requisitos: Python 3.11 o superior.

```bash
git clone <url-del-repositorio>
cd smartcampus

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Ejecución local

Desde la raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Documentación interactiva (Swagger UI): http://127.0.0.1:8000/docs

## Configuración

Los valores que pueden variar entre entornos se leen de variables de entorno:

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `APP_ENV` | Entorno de ejecución | `development` |
| `DB_PATH` | Ruta del fichero SQLite | `app/db/mi_base_de_datos.db` |

```bash
DB_PATH=/data/smartcampus.db uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Las tablas se crean automáticamente al arrancar la aplicación.

## API

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| GET | `/health` | Comprobación de estado | 200 |
| GET | `/rooms` | Lista todas las aulas | 200 |
| GET | `/rooms/{id}` | Consulta un aula por ID | 200, 404 |
| POST | `/rooms` | Registra un aula | 201, 422 |
| DELETE | `/rooms/{id}` | Elimina un aula | 204, 404 |
| GET | `/bookings` | Lista las reservas | 200 |
| POST | `/bookings` | Crea una reserva | 201, 404, 409, 422 |
| DELETE | `/bookings/{id}` | Elimina una reserva | 204, 404 |

### Ejemplos

Crear un aula:

```bash
curl -X POST http://127.0.0.1:8000/rooms \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laboratorio de Robótica",
    "edificio": "Edificio A",
    "capacidad": 30,
    "equipamiento": ["ordenadores", "robots", "impresora 3D"]
  }'
```

Crear una reserva (`aula_id` es el `id` del aula; el `id` de la reserva lo genera la base de datos):

```bash
curl -X POST http://127.0.0.1:8000/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "aula_id": 1,
    "usuario": "ana",
    "fecha": "2026-10-12",
    "hora_inicio": "10:00",
    "hora_fin": "12:00"
  }'
```

## Reglas de negocio

| Regla | Código |
|---|---|
| No se pueden crear aulas con capacidad menor o igual que 0 | 422 |
| No se puede consultar ni eliminar un aula inexistente | 404 |
| No se puede reservar un aula inexistente | 404 |
| La hora de inicio debe ser anterior a la de fin | 422 |
| Las horas deben tener formato `HH:MM` y la fecha `YYYY-MM-DD` | 422 |
| No pueden existir dos reservas solapadas para la misma aula y fecha | 409 |
| No se puede eliminar una reserva inexistente | 404 |

Ejemplo de solape: con una reserva de 10:00 a 12:00 en un aula, otra de 11:00 a 13:00 en la misma aula y fecha se rechaza. Las reservas contiguas (una termina a las 12:00 y otra empieza a las 12:00) sí se permiten.

## Tests

Los tests usan `pytest` y se dividen con marcadores:

- **`unit`** (`tests/test_services.py`): modelos y services, sin HTTP.
- **`integration`** (`tests/test_rooms.py`, `tests/test_bookings.py`, `tests/test_health.py`): endpoints HTTP con `TestClient`.

Cada test usa una base de datos SQLite temporal, así que no toca `app/db/`.

```bash
pytest                    # todos
pytest -m unit            # solo unitarios
pytest -m integration     # solo integración
pytest -v                 # salida detallada
```

Casos de error cubiertos: aula inexistente, reserva solapada, capacidad inválida, ID inexistente, hora incorrecta, formato de fecha y hora inválido, y borrado en cascada.

## Git Hooks

Los hooks están en la carpeta versionada `hooks/`, porque `.git/hooks/` no se sube al repositorio. Se activan con `core.hooksPath`.

### Instalación

Una vez tras clonar el repositorio, con el entorno virtual creado y las dependencias instaladas:

```bash
sh install-hooks.sh
```

El script da permisos de ejecución a los hooks, ejecuta `git config core.hooksPath hooks` y crea el alias `git pushp`.

### Qué hace cada hook

| Hook | Cuándo | Qué hace | Si falla |
|---|---|---|---|
| `pre-commit` | Antes de cada commit | Ejecuta `ruff check`, `ruff format --check` y `pytest -m unit` | `❌ Commit rechazado` y el commit no se crea |
| `post-commit` | Después de cada commit | Añade a `commit-log.txt` autor, hash, mensaje y fecha | — |
| `pre-push` | Antes de cada push | Ejecuta `pytest -m unit` y `pytest -m integration` | `❌ Push rechazado: existen tests fallidos` |
| `post-push` | Después de un push correcto | Muestra `🚀 Cambios enviados correctamente al repositorio remoto.` | — |

### Registro de commits

`post-commit` genera `commit-log.txt` (ignorado por Git) con este formato:

```
Autor: Fer
Hash: a81f32c
Mensaje: feat: add booking endpoints
Fecha: 24/09/2026
---
```

### post-push

Git no incluye un hook `post-push` nativo. Se simula con un alias, `git pushp`, que ejecuta el push y, solo si termina bien, lanza `hooks/post-push`:

```bash
git pushp origin feature/mi-rama
```

Con `git push` a secas se ejecuta igualmente el `pre-push`, pero no el mensaje final.

### Formato del código

La calidad se comprueba con [Ruff](https://docs.astral.sh/ruff/) (configuración en `ruff.toml`). Para corregir los avisos automáticamente:

```bash
ruff check --fix .
ruff format .
```

## Docker

La imagen parte de `python:3.12-slim`. Copia primero `requirements.txt` para aprovechar la caché de capas, corre con un usuario no root (`appuser`) y guarda la base de datos SQLite en `/data` (`DB_PATH=/data/smartcampus.db`).

```bash
docker build -t smartcampus .
docker run -p 8000:8000 smartcampus
```

La API queda en http://localhost:8000 (Swagger en `/docs`). Sin volumen, los datos se pierden al borrar el contenedor; para conservarlos: `docker run -p 8000:8000 -v smartcampus-data:/data smartcampus`.

## Docker Compose

Levanta la aplicación con su configuración, red, volumen y healthcheck:

```bash
cp .env.example .env
docker compose up --build
```

| Variable (`.env`) | Descripción |
|---|---|
| `APP_ENV` | Entorno de ejecución |
| `APP_PORT` | Puerto publicado en el equipo (por defecto 8000) |
| `DB_PATH` | Ruta del SQLite dentro del contenedor |

El servicio `backend` usa:

- **Variables:** se leen del `.env` (que no se sube a Git; el repositorio incluye `.env.example`).
- **Red:** `smartcampus-net`, propia del proyecto.
- **Volumen:** `smartcampus-data` montado en `/data`, para que la base de datos sobreviva a reinicios y a `docker compose down`.
- **Healthcheck:** cada 10 s llama a `GET /health`; el contenedor pasa a `healthy` cuando responde.
- **Reinicio:** `restart: unless-stopped`.

No hay servicio de base de datos porque se usa SQLite en fichero, por eso tampoco hay `depends_on`. Para parar: `docker compose down` (conserva los datos) o `docker compose down -v` (los borra).

## GitHub Actions

El workflow está en `.github/workflows/ci-cd.yml`.

**Cuándo se ejecuta:** en cada `push` y `pull_request` sobre `main` y `develop`. Los jobs `publish` y `deploy` solo se ejecutan en un `push` a `main`; en las Pull Requests aparecen como _skipped_.

**Etapas:**

| Job | Dónde corre | Qué hace |
|---|---|---|
| `test` | GitHub (ubuntu) | Checkout, instala dependencias, calidad (`ruff check` y `ruff format --check`) y `pytest` |
| `build` | GitHub (ubuntu) | `docker build -t smartcampus .`, arranca el contenedor y comprueba `/health` con `curl` |
| `publish` | GitHub (ubuntu) | Inicia sesión en Docker Hub y publica la imagen (`latest` y el hash del commit) |
| `deploy` | Runner propio (self-hosted) | `docker compose up -d --build` y comprueba `/health` |

Cada job depende del anterior (`needs`): si falla uno, los siguientes no se ejecutan.

**Matrix:** el job `test` se ejecuta con Python 3.11 y 3.12 en paralelo, para comprobar que la aplicación funciona en ambas versiones.

**Variables:** el workflow define `APP_ENV` con `env:`. En el despliegue se genera un `.env` de producción con `APP_ENV=production`, `APP_PORT` y `DB_PATH`.

**Secrets:** se usan `DOCKER_USERNAME` y `DOCKER_PASSWORD` (un token de acceso de Docker Hub, no la contraseña). Se guardan en Settings → Secrets and variables → Actions, solo se leen en el job `publish`, no aparecen en el código ni en el repositorio, y GitHub los oculta en los logs.

**Despliegue:** se hace con un _self-hosted runner_ (opción A del enunciado) instalado en el equipo que actúa como servidor. Cuando se actualiza `main`, GitHub le envía el job `deploy` y el runner levanta la aplicación con Docker Compose en ese equipo, accesible en http://localhost:8000. El runner debe estar en marcha (`./run.sh` dentro de `actions-runner`) para que el despliegue se ejecute.

## Flujo de trabajo en Git

- `main`: rama estable.
- `develop`: rama de integración.
- `feature/...`: una rama por bloque de trabajo, que se integra en `develop` mediante Pull Request revisada por el otro miembro del equipo.

Mensajes de commit: `feat:`, `test:`, `ci:`, `docker:`, `docs:`, `style:`.

## Evidencias

Las capturas se guardan en `docs/img/`.

| Evidencia | Estado |
|---|---|
| Aplicación funcionando (Swagger `/docs`) | _pendiente_ |
| Errores 404, 409 y 422 | _pendiente_ |
| Tests en verde (`pytest -v`) | _pendiente_ |
| `pre-commit` aceptando un commit | _pendiente_ |
| `pre-commit` rechazando un commit | _pendiente_ |
| `post-commit` (`commit-log.txt`) | _pendiente_ |
| `pre-push` rechazando un push | _pendiente_ |
| `pre-push` aceptando + `post-push` (`git pushp`) | _pendiente_ |
| Imagen Docker construida | [captura](docs/img/docker-compose-healthy.png) |
| Docker Compose en ejecución | [captura](docs/img/docker-compose-healthy.png) |
| Pipeline de GitHub Actions ejecutado (test, build, publish y deploy) | [captura](docs/img/pipeline-main-completo.png) |
| Matrix (Python 3.11 y 3.12) | [captura](docs/img/pipeline-verde-matrix.png) |
| Imagen publicada en Docker Hub | [captura](docs/img/publish-summary.png) |
| GitHub Secrets configurados (sin valores) | [captura](docs/img/secrets-configurados.png) |
| Runner self-hosted activo | [captura](docs/img/runner-idle.png) |
| Aplicación desplegada | [captura](docs/img/app-desplegada-swagger.png) |