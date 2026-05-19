"""Evidencia schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EvidenciaUpload(BaseModel):
    """Schema for file upload metadata (actual file is multipart)."""
    campo_id: Optional[UUID] = None


class EvidenciaResponse(BaseModel):
    """Schema for evidencia response."""
    id: UUID
    fase_id: UUID
    campo_id: Optional[UUID]
    nombre_archivo: str
    ruta_storage: str
    tipo_mime: Optional[str]
    tamano_bytes: Optional[int]
    uploaded_by: Optional[UUID]
    created_at: datetime
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)