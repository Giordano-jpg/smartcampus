# SmartCampus

Microservicio REST para la gestión de aulas y reservas de espacios universitarios, desarrollado para SmartCampus Solutions como parte de la Práctica 1 (automatización y despliegue con Git Hooks y GitHub Actions).

> **Estado del proyecto:** en desarrollo. Las secciones marcadas como _pendiente_ se completarán conforme avance la práctica.

## Descripción

SmartCampus permite a una universidad gestionar sus aulas (nombre, edificio, capacidad y equipamiento) y las reservas de esos espacios. El objetivo de la práctica no es solo la aplicación, sino el flujo de automatización que la rodea: Git Hooks, tests, Docker y un pipeline de CI/CD con GitHub Actions.

## Arquitectura

El proyecto sigue una arquitectura por capas, sin vistas (es una API REST):

```
Cliente → Router (FastAPI) → Service (lógica y SQL) → SQLite
```

```
smartcampus/
├── app/
│   ├── __init__.py
│   ├── main.py          # crea la app FastAPI, registra routers y /health
│   ├── config.py        # configuración por variables de entorno
│   ├── database.py      # conexión SQLite y creación de tablas
│   ├── models.py        # esquemas Pydantic (Room, RoomCreate)
│   ├── services.py      # lógica de negocio y consultas SQL
│   ├── routers/
│   │   ├── __init__.py
│   │   └── rooms.py     # endpoints de aulas
│   └── db/              # fichero SQLite (ignorado por Git)
├── tests/               # _pendiente_
├── requirements.txt
└── README.md
```

- **Routers**: reciben la petición HTTP, llaman a los services y traducen los errores a códigos HTTP.
- **Services**: contienen las reglas de negocio y el SQL. Se pueden probar sin pasar por HTTP.
- **Base de datos**: SQLite con el módulo `sqlite3` de la librería estándar, sin ORM.

### Modelo de datos

**Aula (`rooms`)**: `id`, `nombre`, `edificio`, `capacidad`, `equipamiento` (lista guardada como JSON).

**Reserva (`bookings`)**: `id`, `aula_id`, `usuario`, `fecha`, `hora_inicio`, `hora_fin` (_endpoints pendientes_).

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

Ejemplo:

```bash
DB_PATH=/data/smartcampus.db uvicorn app.main:app
```

Las tablas se crean automáticamente al arrancar la aplicación.

## API

### Implementados

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| GET | `/health` | Comprobación de estado | 200 |
| GET | `/rooms` | Lista todas las aulas | 200 |
| GET | `/rooms/{id}` | Consulta un aula por ID | 200, 404 |
| POST | `/rooms` | Registra un aula | 201, 422 |
| DELETE | `/rooms/{id}` | Elimina un aula | 204, 404 |

### Pendientes

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/bookings` | Lista las reservas |
| POST | `/bookings` | Crea una reserva |
| DELETE | `/bookings/{id}` | Elimina una reserva |

### Ejemplo

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

```json
{
  "id": 1,
  "nombre": "Laboratorio de Robótica",
  "edificio": "Edificio A",
  "capacidad": 30,
  "equipamiento": ["ordenadores", "robots", "impresora 3D"]
}
```

## Reglas de negocio

### Implementadas

- No se pueden crear aulas con capacidad menor o igual que 0 (validación Pydantic, error 422, y `CHECK` en SQL).
- No se puede consultar ni eliminar un aula inexistente (error 404).

### Pendientes (reservas)

- No se puede reservar un aula inexistente (404).
- La hora de inicio debe ser anterior a la de fin (422).
- No pueden existir dos reservas solapadas para la misma aula (409).
- No se puede eliminar una reserva inexistente (404).

## Tests

_Pendiente._ Se utilizará `pytest`, con tests unitarios (services) y de integración (endpoints).

```bash
pytest
```

## Git Hooks

_Pendiente._ Se documentarán `pre-commit`, `post-commit`, `pre-push` y `post-push`.

## Docker y Docker Compose

_Pendiente._

## GitHub Actions

_Pendiente._

## Flujo de trabajo en Git

- `main`: rama estable.
- `develop`: rama de integración.
- `feature/...`: una rama por bloque de trabajo, que se integra en `develop` mediante Pull Request.

Los mensajes de commit siguen el formato `feat:`, `test:`, `ci:`, `docker:`, `docs:`.

## Evidencias

_Pendiente._ Se añadirán capturas de la aplicación, tests, hooks, Docker, pipeline, matrix y despliegue.