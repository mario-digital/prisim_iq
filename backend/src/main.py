"""PrismIQ Backend - FastAPI Application Entry Point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.middleware import LoggingMiddleware, TimingMiddleware
from src.api.routers import chat, data, evidence, explain, external, health, pricing, sensitivity
from src.config import get_settings
from src.schemas.data import ErrorResponse
from src.services.sensitivity_service import shutdown_sensitivity_service


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    settings = get_settings()
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    yield
    # Shutdown
    logger.info("Shutting down PrismIQ API")
    # Gracefully shutdown ProcessPoolExecutor to prevent orphaned workers
    shutdown_sensitivity_service(wait=True)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="AI-powered dynamic pricing assistant with explainable recommendations",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Register exception handlers
    _register_exception_handlers(app)

    # Add middleware (order matters: last added = first executed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TimingMiddleware)
    app.add_middleware(LoggingMiddleware)

    # Include routers
    app.include_router(health.router)
    app.include_router(data.router, prefix="/api/v1")
    app.include_router(pricing.router, prefix="/api/v1")
    app.include_router(explain.router, prefix="/api/v1")
    app.include_router(sensitivity.router, prefix="/api/v1")
    app.include_router(evidence.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(external.router, prefix="/api/v1")

    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers."""

    @app.exception_handler(ValueError)
    async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError as 400 Bad Request."""
        logger.warning(f"ValueError: {exc}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                detail=str(exc),
                error_code="VALIDATION_ERROR",
            ).model_dump(),
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(_request: Request, exc: FileNotFoundError) -> JSONResponse:
        """Handle FileNotFoundError as 404 Not Found."""
        logger.warning(f"FileNotFoundError: {exc}")
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                detail=str(exc),
                error_code="RESOURCE_NOT_FOUND",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions as 500 Internal Server Error."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                detail="Internal server error",
                error_code="INTERNAL_ERROR",
            ).model_dump(),
        )


# Create the application instance
app = create_app()


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
