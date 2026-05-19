"""Evidencia model."""
import uuid
from datetime import datetime

from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Evidencia(Base):
    """Archivo de evidencia asociado a una fase o campo."""

    __tablename__ = "evidencias"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    fase_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fases.id", ondelete="CASCADE"),
        nullable=False,
    )
    campo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campos.id", ondelete="SET NULL"),
        nullable=True,
    )
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    ruta_storage: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_mime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tamano_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    fase: Mapped["Fase"] = relationship("Fase", back_populates="evidencias")
    campo: Mapped["Campo | None"] = relationship("Campo", back_populates="evidencias")
    uploader: Mapped["User | None"] = relationship("User", foreign_keys=[uploaded_by])


# Import for type hints
from app.models.fase import Fase
from app.models.campo import Campo
from app.models.user import User