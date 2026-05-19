"""Fase schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import EstadoExpediente


class FaseUpdate(BaseModel):
    """Schema for updating fase."""
    nombre: Optional[str] = None
    estado: Optional[EstadoExpediente] = None


class CampoSummary(BaseModel):
    """Summary of campo."""
    id: UUID
    clave: str
    valor: Optional[str]
    tipo: str

    model_config = ConfigDict(from_attributes=True)


class EvidenciaSummary(BaseModel):
    """Summary of evidencia."""
    id: UUID
    nombre_archivo: str
    tipo_mime: Optional[str]
    tamano_bytes: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ObservacionSummary(BaseModel):
    """Summary of observacion."""
    id: UUID
    tipo: str
    contenido: str
    revisada: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FaseResponse(BaseModel):
    """Schema for fase response."""
    id: UUID
    expediente_id: UUID
    numero: int
    nombre: str
    estado: EstadoExpediente
    completada: bool
    created_at: datetime
    updated_at: datetime
    campos: list[CampoSummary] = []
    evidencias: list[EvidenciaSummary] = []
    observaciones: list[ObservacionSummary] = []

    model_config = ConfigDict(from_attributes=True)