"""Observacion schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import TipoObservacion


class ObservacionCreate(BaseModel):
    """Schema for creating an observacion."""
    tipo: TipoObservacion
    contenido: str


class ObservacionUpdate(BaseModel):
    """Schema for updating an observacion."""
    revisada: bool


class ObservacionResponse(BaseModel):
    """Schema for observacion response."""
    id: UUID
    fase_id: UUID
    autor_id: Optional[UUID]
    tipo: TipoObservacion
    contenido: str
    revisada: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)