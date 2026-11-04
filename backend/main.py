import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from database import engine
from realtime.manager import manager
from realtime.ws_routes import router as ws_router
from models.user import User  # noqa: F401 - registers table with SQLModel metadata
from models.module import Module  # noqa: F401 - registers table with SQLModel metadata
from models.sub_module import SubModule  # noqa: F401 - registers table with SQLModel metadata
from models.progress import Progress  # noqa: F401 - registers table with SQLModel metadata
from models.bug_trigger import BugTrigger  # noqa: F401 - registers table with SQLModel metadata
from models.spark_term import SparkTerm  # noqa: F401 - registers table with SQLModel metadata
from models.byte_fact import ByteFact  # noqa: F401 - registers table with SQLModel metadata
from models.challenge import Challenge  # noqa: F401 - registers table with SQLModel metadata
from models.completed_challenge import CompletedChallenge  # noqa: F401 - registers table with SQLModel metadata
from models.badge import Badge  # noqa: F401 - registers table with SQLModel metadata
from models.user_badge import UserBadge  # noqa: F401 - registers table with SQLModel metadata
from models.certificate import Certificate  # noqa: F401 - registers table with SQLModel metadata
from models.submission import Submission  # noqa: F401 - registers table with SQLModel metadata
from routes import (
    user_router,
    module_router,
    sub_module_router,
    progression_router,
    progress_router,
    bug_trigger_router,
    spark_term_router,
    byte_fact_router,
    challenge_router,
    submission_router,
)


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS")
    if raw is None:
        return ["http://localhost:3000"]
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    origins = [origin for origin in origins if origin != "*"]
    if not origins:
        return ["http://localhost:3000"]
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables if they do not exist
    SQLModel.metadata.create_all(engine)
    manager.loop = asyncio.get_running_loop()
    yield


app = FastAPI(lifespan=lifespan)

# Cross-Origin Resource Sharing (CORS) is a browser security mechanism that restricts
# web applications from making requests to a domain different from the one that served the application.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(user_router)
app.include_router(module_router)
app.include_router(sub_module_router)
app.include_router(progression_router)
app.include_router(progress_router)
app.include_router(bug_trigger_router)
app.include_router(spark_term_router)
app.include_router(byte_fact_router)
app.include_router(challenge_router)
app.include_router(submission_router)
app.include_router(ws_router)


@app.get("/")
def read_root():
    return {
        "name": "SetuAI Backend API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
