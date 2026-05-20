"""Audit and version history router."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, Version, Expediente

router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/expedientes/{expediente_id}/audit")
def get_expediente_audit(expediente_id: UUID, db: Session = Depends(get_db)):
    """Get audit log for an expediente and its related entities."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    # Get all audit logs related to this expediente (fases, evidencias, etc)
    # We need to join through entity_id - this is a simplified approach
    audit_logs = db.query(AuditLog).join(
        Version, Version.entity_id == AuditLog.entity_id, isouter=True
    ).filter(
        (AuditLog.entity == "Expediente") & (AuditLog.entity_id == expediente_id) |
        (Version.expediente_id == expediente_id)
    ).order_by(AuditLog.created_at.desc()).limit(100).all()

    return [
        {
            "id": str(log.id),
            "action": log.action.value,
            "entity": log.entity,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "created_at": log.created_at.isoformat(),
        }
        for log in audit_logs
    ]


@router.get("/expedientes/{expediente_id}/versiones")
def get_expediente_versiones(expediente_id: UUID, db: Session = Depends(get_db)):
    """Get version history for an expediente."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    versiones = db.query(Version).filter(
        Version.expediente_id == expediente_id
    ).order_by(Version.numero.desc()).all()

    return [
        {
            "id": str(v.id),
            "numero": v.numero,
            "fase_id": str(v.fase_id) if v.fase_id else None,
            "cambios": v.cambios,
            "created_at": v.created_at.isoformat(),
        }
        for v in versiones
    ]