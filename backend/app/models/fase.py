"""Fase model."""
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import EstadoExpediente


class Fase(Base):
    """Fase institucional del expediente."""

    __tablename__ = "fases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    expediente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("expedientes.id", ondelete="CASCADE"),
        nullable=False,
    )
    numero: Mapped[int] = mapped_column(nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[EstadoExpediente] = mapped_column(
        String(50),
        default=EstadoExpediente.BORRADOR,
    )
    completada: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("expediente_id", "numero"),
    )

    # Relationships
    expediente: Mapped["Expediente"] = relationship(
        "Expediente",
        back_populates="fases",
    )
    campos: Mapped[list["Campo"]] = relationship(
        "Campo",
        back_populates="fase",
        cascade="all, delete-orphan",
    )
    evidencias: Mapped[list["Evidencia"]] = relationship(
        "Evidencia",
        back_populates="fase",
        cascade="all, delete-orphan",
    )
    observaciones: Mapped[list["Observacion"]] = relationship(
        "Observacion",
        back_populates="fase",
        cascade="all, delete-orphan",
        order_by="Observacion.created_at",
    )


# Import for type hints
from app.models.expediente import Expediente
from app.models.campo import Campo
from app.models.evidencia import Evidencia
from app.models.observacion import Observacion