"""Expedientes router."""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Expediente, Fase
from app.models.enums import FASES_INSTITUCIONALES, EstadoExpediente
from app.schemas.expediente import (
    ExpedienteCreate,
    ExpedienteUpdate,
    ExpedienteResponse,
    ExpedienteListResponse,
)
from app.services.audit import AuditService
from app.services.ia_fase import auto_fill_expediente_fases_sync

router = APIRouter(prefix="/api/expedientes", tags=["expedientes"])


def calculate_progress(expediente: Expediente) -> int:
    """Calculate progress percentage based on completed fases."""
    if not expediente.fases:
        return 0
    completed = sum(1 for f in expediente.fases if f.completada)
    return int((completed / len(expediente.fases)) * 100)


@router.post("", response_model=ExpedienteResponse, status_code=201)
def create_expediente(
    expediente: ExpedienteCreate,
    db: Session = Depends(get_db),
):
    """Create a new expediente with 10 fases."""
    # Create expediente
    db_expediente = Expediente(
        tipo_tramite=expediente.tipo_tramite,
        nombre_programa=expediente.nombre_programa,
        facultad=expediente.facultad,
        nivel=expediente.nivel,
        modalidad=expediente.modalidad,
        lugar_desarrollo=expediente.lugar_desarrollo,
        proposito=expediente.proposito,
    )
    db.add(db_expediente)
    db.flush()

    # Auto-create 10 fases
    for i, nombre in enumerate(FASES_INSTITUCIONALES, start=1):
        fase = Fase(
            expediente_id=db_expediente.id,
            numero=i,
            nombre=nombre,
            estado=EstadoExpediente.BORRADOR,
        )
        db.add(fase)

    db.commit()
    db.refresh(db_expediente)

    # Auto-fill all phases with AI suggestions
    try:
        auto_fill_expediente_fases_sync(str(db_expediente.id), db)
    except Exception as e:
        print(f"Auto-fill warning: {e}")

    # Log audit
    audit = AuditService(db)
    audit.log_create(
        entity="Expediente",
        entity_id=db_expediente.id,
        new_values={"nombre_programa": expediente.nombre_programa},
    )

    # Refresh to get filled campos
    db.refresh(db_expediente)
    response = ExpedienteResponse.model_validate(db_expediente)
    response.progreso = calculate_progress(db_expediente)
    return response


@router.get("", response_model=list[ExpedienteListResponse])
def list_expedientes(
    estado: Optional[EstadoExpediente] = Query(None),
    tipo_tramite: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all expedientes with optional filters."""
    query = db.query(Expediente).options(joinedload(Expediente.fases))

    if estado:
        query = query.filter(Expediente.estado == estado)
    if tipo_tramite:
        query = query.filter(Expediente.tipo_tramite == tipo_tramite)

    expedientes = query.order_by(Expediente.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for exp in expedientes:
        resp = ExpedienteListResponse.model_validate(exp)
        resp.progreso = calculate_progress(exp)
        result.append(resp)

    return result


@router.get("/{expediente_id}", response_model=ExpedienteResponse)
def get_expediente(expediente_id: UUID, db: Session = Depends(get_db)):
    """Get a single expediente by ID."""
    expediente = db.query(Expediente).options(
        joinedload(Expediente.fases)
    ).filter(Expediente.id == expediente_id).first()

    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    response = ExpedienteResponse.model_validate(expediente)
    response.progreso = calculate_progress(expediente)
    return response


@router.put("/{expediente_id}", response_model=ExpedienteResponse)
def update_expediente(
    expediente_id: UUID,
    expediente: ExpedienteUpdate,
    db: Session = Depends(get_db),
):
    """Update an expediente."""
    db_expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()

    if not db_expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    if db_expediente.estado != EstadoExpediente.BORRADOR:
        raise HTTPException(
            status_code=403,
            detail="No se puede editar un expediente que no está en estado BORRADOR",
        )

    # Track old values for audit
    old_values = {
        "nombre_programa": db_expediente.nombre_programa,
        "estado": db_expediente.estado,
    }

    # Update fields
    update_data = expediente.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expediente, field, value)

    db.commit()
    db.refresh(db_expediente)

    # Log audit
    audit = AuditService(db)
    audit.log_update(
        entity="Expediente",
        entity_id=db_expediente.id,
        old_values=old_values,
        new_values=update_data,
    )

    response = ExpedienteResponse.model_validate(db_expediente)
    response.progreso = calculate_progress(db_expediente)
    return response


@router.delete("/{expediente_id}", status_code=204)
def delete_expediente(expediente_id: UUID, db: Session = Depends(get_db)):
    """Delete an expediente (only if in BORRADOR state)."""
    db_expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()

    if not db_expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    if db_expediente.estado != EstadoExpediente.BORRADOR:
        raise HTTPException(
            status_code=403,
            detail="Solo se pueden eliminar expedientes en estado BORRADOR",
        )

    old_values = {"nombre_programa": db_expediente.nombre_programa}

    audit = AuditService(db)
    audit.log_delete(
        entity="Expediente",
        entity_id=db_expediente.id,
        old_values=old_values,
    )

    db.delete(db_expediente)
    db.commit()


@router.get("/{expediente_id}/tablero")
def get_tablero(expediente_id: UUID, db: Session = Depends(get_db)):
    """Get dashboard data for an expediente."""
    expediente = db.query(Expediente).options(
        joinedload(Expediente.fases).joinedload(Fase.observaciones)
    ).filter(Expediente.id == expediente_id).first()

    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    fases_data = []
    for fase in sorted(expediente.fases, key=lambda f: f.numero):
        pendientes = [o for o in fase.observaciones if not o.revisada]
        estado_val = fase.estado.value if hasattr(fase.estado, 'value') else fase.estado
        fases_data.append({
            "id": str(fase.id),
            "numero": fase.numero,
            "nombre": fase.nombre,
            "estado": estado_val,
            "completada": fase.completada,
            "observaciones_pendientes": len(pendientes),
        })

    return {
        "expediente_id": str(expediente_id),
        "nombre_programa": expediente.nombre_programa,
        "estado": expediente.estado.value if hasattr(expediente.estado, 'value') else expediente.estado,
        "progreso": calculate_progress(expediente),
        "fases": fases_data,
    }