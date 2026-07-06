from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app.api.router import api_router

from app.models.user import User
from app.models.job import Job
from app.models.embedding import ChunkEmbedding
from app.models.qa_session import QASession
from app.models.guide import Guide

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup actions on startup
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup actions on shutdown
    await engine.dispose()

app = FastAPI(
    title="AntiRAGing API",
    description="Codebase Onboarding Agent Backend",
    version="1.0.0",
    lifespan=lifespan
)

from app.config import settings

# CORS middleware
origins = ["http://localhost:3000"]
if settings.frontend_url != "http://localhost:3000" and settings.frontend_url != "*":
    origins.append(settings.frontend_url.rstrip("/"))
elif settings.frontend_url == "*":
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
