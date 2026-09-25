from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine
from models.user import User  # noqa: F401 - registers table with SQLModel metadata
from models.module import Module  # noqa: F401 - registers table with SQLModel metadata
from models.sub_module import SubModule  # noqa: F401 - registers table with SQLModel metadata
from models.progress import Progress  # noqa: F401 - registers table with SQLModel metadata
from models.bug_trigger import BugTrigger  # noqa: F401 - registers table with SQLModel metadata
from models.spark_term import SparkTerm  # noqa: F401 - registers table with SQLModel metadata
from models.byte_fact import ByteFact  # noqa: F401 - registers table with SQLModel metadata
from routes import (
    user_router,
    module_router,
    sub_module_router,
    progress_router,
    bug_trigger_router,
    spark_term_router,
    byte_fact_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables if they do not exist
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(module_router)
app.include_router(sub_module_router)
app.include_router(progress_router)
app.include_router(bug_trigger_router)
app.include_router(spark_term_router)
app.include_router(byte_fact_router)


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
