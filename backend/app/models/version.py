"""Version model."""
import uuid
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Version(Base):
    """Registro de versión/historial de cambios."""

    __tablename__ = "versiones"

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
    fase_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fases.id", ondelete="SET NULL"),
        nullable=True,
    )
    cambios: Mapped[dict] = mapped_column(JSON, nullable=False)
    creado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    expediente: Mapped["Expediente"] = relationship(
        "Expediente",
        back_populates="versiones",
    )
    fase: Mapped["Fase | None"] = relationship("Fase")
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[creado_por])


# Import for type hints
from app.models.expediente import Expediente
from app.models.fase import Fase
from app.models.user import User