"""FastAPI application entrypoint."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, bugs, challenges, users, xp
from app.core.config import settings
from app.middleware.error_handling import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Bug Hunter Arena API — a gamified QA/testing learning platform.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(challenges.router, prefix=settings.API_V1_PREFIX)
app.include_router(bugs.router, prefix=settings.API_V1_PREFIX)
app.include_router(xp.router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"], summary="Liveness probe")
def health():
    return {"status": "ok"}
