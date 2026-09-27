"""
ChangeBlast — FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload

The application factory pattern is used so that the `app` object is fully
configured before it is handed to Uvicorn, making it straightforward to
reuse in tests.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic (database pool, caches, etc.)."""
    # TODO: initialise resources on startup (e.g. warm connection pool).
    yield
    # TODO: clean up resources on shutdown.


# ── Application factory ───────────────────────────────────────────────────────
def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="See the blast radius before you change the code.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    application.include_router(api_v1_router, prefix="/api/v1")

    return application


app = create_app()
