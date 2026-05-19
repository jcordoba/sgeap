"""Observaciones router."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Observacion, Fase
from app.models.enums import TipoObservacion, EstadoExpediente
from app.schemas.observacion import ObservacionCreate, ObservacionUpdate, ObservacionResponse
from app.services.audit import AuditService

router = APIRouter(prefix="/api", tags=["observaciones"])


def get_fase_or_404(db: Session, fase_id: UUID) -> Fase:
    """Helper to get fase or raise 404."""
    fase = db.query(Fase).filter(Fase.id == fase_id).first()
    if not fase:
        raise HTTPException(status_code=404, detail="Fase no encontrada")
    return fase


@router.post("/fases/{fase_id}/observaciones", response_model=ObservacionResponse, status_code=201)
def create_observacion(
    fase_id: UUID,
    observacion: ObservacionCreate,
    db: Session = Depends(get_db),
):
    """Create an observation for a fase."""
    fase = get_fase_or_404(db, fase_id)

    db_observacion = Observacion(
        fase_id=fase_id,
        tipo=observacion.tipo,
        contenido=observacion.contenido,
    )
    db.add(db_observacion)

    # Trigger state changes based on tipo
    if observacion.tipo == TipoObservacion.DEVOLUCION:
        fase.estado = EstadoExpediente.CON_OBSERVACIONES
        fase.completada = False
    elif observacion.tipo == TipoObservacion.APROBACION:
        fase.estado = EstadoExpediente.VALIDADO_TECNICAMENTE
        fase.completada = True

    db.commit()
    db.refresh(db_observacion)

    # Log audit
    audit = AuditService(db)
    audit.log_create(
        entity="Observacion",
        entity_id=db_observacion.id,
        new_values={
            "tipo": observacion.tipo.value,
            "fase_id": str(fase_id),
        },
    )

    return ObservacionResponse.model_validate(db_observacion)


@router.get("/fases/{fase_id}/observaciones", response_model=list[ObservacionResponse])
def list_observaciones(fase_id: UUID, db: Session = Depends(get_db)):
    """List all observaciones for a fase."""
    fase = get_fase_or_404(db, fase_id)

    observaciones = db.query(Observacion).filter(
        Observacion.fase_id == fase_id
    ).order_by(Observacion.created_at.desc()).all()

    return [ObservacionResponse.model_validate(o) for o in observaciones]


@router.put("/observaciones/{observacion_id}/revisada", response_model=ObservacionResponse)
def mark_revisada(
    observacion_id: UUID,
    data: ObservacionUpdate,
    db: Session = Depends(get_db),
):
    """Mark an observation as reviewed."""
    observacion = db.query(Observacion).filter(Observacion.id == observacion_id).first()

    if not observacion:
        raise HTTPException(status_code=404, detail="Observación no encontrada")

    old_revisada = observacion.revisada
    observacion.revisada = data.revisada

    db.commit()
    db.refresh(observacion)

    # Log audit
    audit = AuditService(db)
    audit.log_update(
        entity="Observacion",
        entity_id=observacion.id,
        old_values={"revisada": old_revisada},
        new_values={"revisada": data.revisada},
    )

    return ObservacionResponse.model_validate(observacion)