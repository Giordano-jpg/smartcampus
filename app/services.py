import json

from app.sqlite import get_connection
from app.models import Booking, BookingCreate, Room, RoomCreate


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

# -----------------------------------------------------

class BookingNotFoundError(Exception):
    pass


class BookingOverlapError(Exception):
    pass



def _row_to_booking(row) -> Booking:
    return Booking(
        id=row["id"],
        aula_id=row["aula_id"],
        usuario=row["usuario"],
        fecha=row["fecha"],
        hora_inicio=row["hora_inicio"],
        hora_fin=row["hora_fin"]
    )

def _has_overlap(aula_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM bookings "
            "WHERE aula_id = ? AND fecha = ? AND ? < hora_fin AND ? > hora_inicio "
            "LIMIT 1",
            (aula_id, fecha, hora_inicio, hora_fin),
        ).fetchone()
        return row is not None
    finally:
        conn.close()

def create_booking(data: BookingCreate) -> Booking:
    get_room(data.aula_id) # verificar que existe el room
    conn = get_connection()
    try:
        if _has_overlap(data.aula_id, data.fecha, data.hora_inicio, data.hora_fin):
            raise BookingOverlapError()
        cur = conn.execute("INSERT INTO bookings (aula_id, fecha, usuario, hora_inicio, hora_fin) VALUES (?, ?, ?, ?, ?)", 
                        (data.aula_id, data.fecha, data.usuario, data.hora_inicio, data.hora_fin),)
        conn.commit()
        return get_booking(cur.lastrowid)
    finally:
        conn.close()

def list_bookings() -> list[Booking]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM bookings ORDER BY id").fetchall()
        return [_row_to_booking(r) for r in rows]
    finally:
        conn.close()


def get_booking(booking_id: int) -> Booking:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM bookings WHERE id = ?", (booking_id,)
        ).fetchone()
        if row is None:
            raise BookingNotFoundError(booking_id)
        return _row_to_booking(row)
    finally:
        conn.close()


def delete_booking(booking_id: int) -> None:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise BookingNotFoundError(booking_id)
    finally:
        conn.close()