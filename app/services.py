import json

from app.sqlite import get_connection
from app.models import Room, RoomCreate


class RoomNotFoundError(Exception):
    pass

def _row_to_room(row) -> Room:
    return Room(
        id=row["id"],
        nombre=row["nombre"],
        edificio=row["edificio"],
        capacidad=row["capacidad"],
        equipamiento=json.loads(row["equipamiento"]),
    )

def create_room(data:RoomCreate) -> Room:
    conn = get_connection()

    try:
        cur = conn.execute("INSERT INTO rooms (nombre, edificio, capacidad, equipamiento)"
                            "VALUES (?,?,?,?)",
        (data.nombre, data.edificio, data.capacidad, json.dumps(data.equipamiento)))

        conn.commit()
        return get_room(cur.lastrowid)

    finally:
        conn.close()


def list_rooms() -> list[Room]:
    conn = get_connection()

    try:
        rows = conn.execute("SELECT * FROM rooms ORDER BY id").fetchall()
        return [_row_to_room(r) for r in rows]
    finally:
        conn.close()

def get_room(room_id: int) -> Room:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM rooms WHERE id = ?", (room_id,)
        ).fetchone()
        if row is None:
            raise RoomNotFoundError(room_id)
        return _row_to_room(row)
    finally:
        conn.close()

def delete_room(room_id:int) -> None:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM ROOMS WHERE id = ?", (room_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise RoomNotFoundError(room_id)
    finally:
        conn.close()



