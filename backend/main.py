from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine
from models.user import User  # noqa: F401 - registers table with SQLModel metadata
from routes import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables if they do not exist
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
