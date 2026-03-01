"""
Main FastAPI application for AI Legal Research Assistant.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.logging_config import logger
from api.routes import router


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    AI Legal Research Assistant with advanced features:
    - Hybrid search (vector + keyword)
    - Document upload and indexing
    - Case summarization
    - Source citations
    - Multi-document retrieval
    - Query history
    - Performance logging
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Gemini Model: {settings.gemini_model}")
    logger.info(f"Embedding Model: {settings.embedding_model}")
    logger.info(f"Vector DB Path: {settings.vector_db_path}")
    logger.info(f"Performance Logging: {'Enabled' if settings.enable_performance_logging else 'Disabled'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info(f"Shutting down {settings.api_title}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["api"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


def main():
    """Run the application."""
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
