import sqlite3

conexion = sqlite3.connect("mi_base_de_datos.db")

cursor = conexion.cursor()

cursor.executescript("""
PRAGMA foreign_keys = ON;

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

CREATE INDEX IF NOT EXISTS idx_bookings_aula_fecha
ON bookings (aula_id, fecha);
""")

conexion.commit()
conexion.close()