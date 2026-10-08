from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    nombre: str = Field(min_length=1)
    edificio: str = Field(min_length=1)
    capacidad: int = Field(gt=0)
    equipamiento: list[str] = Field(default_factory=list)


class Room(RoomCreate):
    id: int