"""Campo model."""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Campo(Base):
    """Campo de contenido dentro de una fase."""

    __tablename__ = "campos"

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
    clave: Mapped[str] = mapped_column(String(100), nullable=False)
    valor: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(50), default="TEXT")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    fase: Mapped["Fase"] = relationship("Fase", back_populates="campos")
    evidencias: Mapped[list["Evidencia"]] = relationship(
        "Evidencia",
        back_populates="campo",
    )


# Import for type hints
from app.models.fase import Fase
from app.models.evidencia import Evidencia