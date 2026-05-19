"""Expediente model."""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import EstadoExpediente, TipoTramite


class Expediente(Base):
    """Expediente académico - cabecera del trámite."""

    __tablename__ = "expedientes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tipo_tramite: Mapped[TipoTramite] = mapped_column(String(20), nullable=False)
    nombre_programa: Mapped[str] = mapped_column(String(255), nullable=False)
    facultad: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nivel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modalidad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lugar_desarrollo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    estado: Mapped[EstadoExpediente] = mapped_column(
        String(50),
        default=EstadoExpediente.BORRADOR,
    )
    proposito: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    fases: Mapped[list["Fase"]] = relationship(
        "Fase",
        back_populates="expediente",
        cascade="all, delete-orphan",
        order_by="Fase.numero",
    )
    versiones: Mapped[list["Version"]] = relationship(
        "Version",
        back_populates="expediente",
        cascade="all, delete-orphan",
        order_by="Version.numero",
    )
    responsable: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[responsable_id],
    )


# Import for type hints
from app.models.fase import Fase
from app.models.version import Version
from app.models.audit_log import AuditLog
from app.models.user import User