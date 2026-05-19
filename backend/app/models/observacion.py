"""Observacion model."""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TipoObservacion


class Observacion(Base):
    """Observación o devolución en una fase."""

    __tablename__ = "observaciones"

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
    autor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    tipo: Mapped[TipoObservacion] = mapped_column(
        String(20),
        nullable=False,
    )
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    revisada: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    fase: Mapped["Fase"] = relationship("Fase", back_populates="observaciones")
    autor: Mapped["User | None"] = relationship("User", foreign_keys=[autor_id])


# Import for type hints
from app.models.fase import Fase
from app.models.user import User