import os

APP_ENV = os.getenv("APP_ENV", "development")


def get_db_path() -> str:
    return os.getenv("app/db", "mi_base_de_datos.db")