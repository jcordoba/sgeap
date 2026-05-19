"""Routers module."""
from app.routers.expedientes import router as expedientes_router
from app.routers.fases import router as fases_router
from app.routers.evidencias import router as evidencias_router
from app.routers.observaciones import router as observaciones_router
from app.routers.auth import router as auth_router

__all__ = [
    "expedientes_router",
    "fases_router",
    "evidencias_router",
    "observaciones_router",
    "auth_router",
]