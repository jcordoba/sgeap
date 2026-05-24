"""Documento RAG schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentoRAGBase(BaseModel):
    """Base schema for DocumentoRAG."""
    titulo: str
    tipo_documento: str
    categoria: str
    fuente: str
    url_origen: Optional[str] = None
    contenido: str
    contenido_resumido: Optional[str] = None
    metadatos: Optional[dict] = None
    etiquetas: Optional[list[str]] = None
    vigente: bool = True
    fecha_documento: Optional[datetime] = None


class DocumentoRAGCreate(DocumentoRAGBase):
    """Schema for creating a DocumentoRAG."""
    pass


class DocumentoRAGUpdate(BaseModel):
    """Schema for updating a DocumentoRAG."""
    titulo: Optional[str] = None
    tipo_documento: Optional[str] = None
    categoria: Optional[str] = None
    fuente: Optional[str] = None
    url_origen: Optional[str] = None
    contenido: Optional[str] = None
    contenido_resumido: Optional[str] = None
    metadatos: Optional[dict] = None
    etiquetas: Optional[list[str]] = None
    vigente: Optional[bool] = None
    fecha_documento: Optional[datetime] = None


class DocumentoRAGResponse(BaseModel):
    """Schema for DocumentoRAG response."""
    id: UUID
    titulo: str
    tipo_documento: str
    categoria: str
    fuente: str
    url_origen: Optional[str]
    contenido: str
    contenido_resumido: Optional[str]
    metadatos: Optional[dict]
    etiquetas: Optional[list[str]]
    vigente: bool
    fecha_documento: Optional[datetime]
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)


class BusquedaRAGRequest(BaseModel):
    """Request schema for RAG search."""
    query: str
    categoria: Optional[str] = None
    tipo_documento: Optional[str] = None
    limite: int = 10


class ResultadoBusquedaRAG(BaseModel):
    """Single search result from RAG."""
    id: UUID
    titulo: str
    tipo_documento: str
    categoria: str
    fuente: str
    contenido_resumido: Optional[str]
    snippet: str  # Fragmento relevante de la búsqueda
    relevancia: float  # Score de relevancia (0-1)
    url_origen: Optional[str]


class BusquedaRAGResponse(BaseModel):
    """Response schema for RAG search."""
    resultados: list[ResultadoBusquedaRAG]
    total: int
    query: str
    tiempo_ms: int