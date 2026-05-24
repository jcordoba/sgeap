"""Documento RAG model."""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class DocumentoRAG(Base):
    """Documento institucional para RAG."""

    __tablename__ = "documentos_rag"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    titulo = Column(String(500), nullable=False)
    tipo_documento = Column(String(100), nullable=False)  # politica, resolucion, formato, etc.
    categoria = Column(String(200), nullable=False)  # curricular, calidad, normativo, etc.
    fuente = Column(String(200), nullable=False)  # archivo, sistema, url, etc.
    url_origen = Column(String(1000), nullable=True)

    contenido = Column(Text, nullable=False)  # Texto extraído del documento
    contenido_resumido = Column(Text, nullable=True)  # Resumen para visualización

    metadatos = Column(JSON, nullable=True)  # metadata adicional del documento
    etiquetas = Column(JSON, nullable=True)  # tags para búsqueda

    vigente = Column(Boolean, default=True)  # Si es vigente o histórico
    fecha_documento = Column(DateTime, nullable=True)  # Fecha del documento original

    creado_por = Column(PGUUID(as_uuid=True), nullable=True)  # No default, can be null
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Búsqueda vectorial (cuando se instale pgvector)
    embedding = Column(Text, nullable=True)  # Vector almacenado como JSON

    # Para búsqueda de texto completo
    search_vector = Column(Text, nullable=True)  # Texto normalizado para búsqueda

    def __repr__(self):
        return f"<DocumentoRAG {self.titulo[:50]}>"