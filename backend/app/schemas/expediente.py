"""Expediente schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import EstadoExpediente, TipoTramite


class ExpedienteCreate(BaseModel):
    """Schema for creating an expediente."""
    tipo_tramite: TipoTramite
    nombre_programa: str
    facultad: Optional[str] = None
    nivel: Optional[str] = None
    modalidad: Optional[str] = None
    lugar_desarrollo: Optional[str] = None
    proposito: Optional[str] = None


class ExpedienteUpdate(BaseModel):
    """Schema for updating an expediente."""
    nombre_programa: Optional[str] = None
    facultad: Optional[str] = None
    nivel: Optional[str] = None
    modalidad: Optional[str] = None
    lugar_desarrollo: Optional[str] = None
    proposito: Optional[str] = None
    estado: Optional[EstadoExpediente] = None


class FaseSummary(BaseModel):
    """Summary of fase for expediente response."""
    id: UUID
    numero: int
    nombre: str
    estado: EstadoExpediente
    completada: bool

    model_config = ConfigDict(from_attributes=True)


class ExpedienteResponse(BaseModel):
    """Schema for expediente response."""
    id: UUID
    tipo_tramite: TipoTramite
    nombre_programa: str
    facultad: Optional[str]
    nivel: Optional[str]
    modalidad: Optional[str]
    lugar_desarrollo: Optional[str]
    responsable_id: Optional[UUID]
    estado: EstadoExpediente
    proposito: Optional[str]
    created_at: datetime
    updated_at: datetime
    fases: list[FaseSummary] = []
    progreso: int = 0  # percentage

    model_config = ConfigDict(from_attributes=True)


class ExpedienteListResponse(BaseModel):
    """Schema for list of expedientes."""
    id: UUID
    tipo_tramite: TipoTramite
    nombre_programa: str
    estado: EstadoExpediente
    created_at: datetime
    updated_at: datetime
    progreso: int = 0

    model_config = ConfigDict(from_attributes=True)