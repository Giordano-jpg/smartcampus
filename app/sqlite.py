import sqlite3

from app.config import get_db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT    NOT NULL,
    edificio     TEXT    NOT NULL,
    capacidad    INTEGER NOT NULL CHECK (capacidad > 0),
    equipamiento TEXT    NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS bookings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    aula_id     INTEGER NOT NULL,
    usuario     TEXT    NOT NULL,
    fecha       TEXT    NOT NULL,
    hora_inicio TEXT    NOT NULL,
    hora_fin    TEXT    NOT NULL,
    CHECK (hora_inicio < hora_fin),
    FOREIGN KEY (aula_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bookings_aula_fecha ON bookings (aula_id, fecha);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()