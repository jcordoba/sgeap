"""Campo schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CampoUpdate(BaseModel):
    """Schema for updating a campo."""
    valor: Optional[str] = None
    tipo: Optional[str] = None


class CampoResponse(BaseModel):
    """Schema for campo response."""
    id: UUID
    fase_id: UUID
    clave: str
    valor: Optional[str]
    tipo: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)