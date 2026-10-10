from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers import rooms


from app.sqlite import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="SmartCampus", lifespan=lifespan)
app.include_router(rooms.router)


@app.get("/health")
def health():
    return {"status": "ok"}