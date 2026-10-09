import os

APP_ENV = os.getenv("APP_ENV", "development")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # carpeta app/


def get_db_path() -> str:
    return os.getenv("DB_PATH", os.path.join(BASE_DIR, "db", "mi_base_de_datos.db"))