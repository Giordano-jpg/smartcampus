FROM python:3.12-slim

# Evita .pyc y buffer en logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Primero requirements: aprovecha la cache de capas si el codigo cambia pero las dependencias no
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Usuario no root y carpeta de datos (SQLite) con permisos para ese usuario.
# Un volumen nuevo montado en /data hereda estos permisos.
RUN useradd --create-home appuser \
    && mkdir /data \
    && chown -R appuser /code /data
ENV DB_PATH=/data/smartcampus.db
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
