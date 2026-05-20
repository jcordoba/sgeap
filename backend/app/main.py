"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    expedientes_router,
    fases_router,
    evidencias_router,
    observaciones_router,
    auth_router,
    audit_router,
    documento_router,
    users_router,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de Gestión de Expedientes Académicos para Programas - SGEAP",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(expedientes_router)
app.include_router(fases_router)
app.include_router(evidencias_router)
app.include_router(observaciones_router)
app.include_router(audit_router)
app.include_router(documento_router)
app.include_router(users_router)


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }