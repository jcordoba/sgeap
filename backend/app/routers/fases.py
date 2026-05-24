"""Fases router."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Fase, Expediente
from app.models.enums import EstadoExpediente
from app.schemas.fase import FaseUpdate, FaseResponse
from app.services.audit import AuditService
from app.services.ia_fase import auto_fill_fase_sync, auto_fill_expediente_fases_sync
from app.services.ai_minimax import mejorar_contenido

router = APIRouter(prefix="/api", tags=["fases"])


def get_fase_or_404(db: Session, fase_id: UUID) -> Fase:
    """Helper to get fase or raise 404."""
    fase = db.query(Fase).options(
        joinedload(Fase.campos),
        joinedload(Fase.evidencias),
        joinedload(Fase.observaciones),
    ).filter(Fase.id == fase_id).first()

    if not fase:
        raise HTTPException(status_code=404, detail="Fase no encontrada")
    return fase


@router.get("/expedientes/{expediente_id}/fases", response_model=list[FaseResponse])
def list_fases(expediente_id: UUID, db: Session = Depends(get_db)):
    """List all fases for an expediente."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    fases = db.query(Fase).filter(
        Fase.expediente_id == expediente_id
    ).order_by(Fase.numero).all()

    return [FaseResponse.model_validate(f) for f in fases]


@router.get("/fases/{fase_id}", response_model=FaseResponse)
def get_fase(fase_id: UUID, db: Session = Depends(get_db)):
    """Get a single fase by ID."""
    fase = get_fase_or_404(db, fase_id)
    return FaseResponse.model_validate(fase)


@router.put("/fases/{fase_id}", response_model=FaseResponse)
def update_fase(
    fase_id: UUID,
    fase_data: FaseUpdate,
    db: Session = Depends(get_db),
):
    """Update a fase."""
    fase = get_fase_or_404(db, fase_id)

    old_values = {"estado": fase.estado.value}

    update_data = fase_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fase, field, value)

    db.commit()
    db.refresh(fase)

    # Log audit
    audit = AuditService(db)
    audit.log_update(
        entity="Fase",
        entity_id=fase.id,
        old_values=old_values,
        new_values=update_data,
    )

    return FaseResponse.model_validate(fase)


@router.put("/fases/{fase_id}/estado", response_model=FaseResponse)
def update_fase_estado(
    fase_id: UUID,
    estado: EstadoExpediente,
    db: Session = Depends(get_db),
):
    """Update fase estado."""
    fase = get_fase_or_404(db, fase_id)

    old_estado = fase.estado
    fase.estado = estado

    # Update completada based on estado
    if estado in [EstadoExpediente.VALIDADO_TECNICAMENTE, EstadoExpediente.PENDIENTE_APROBACION,
                 EstadoExpediente.APROBADO]:
        fase.completada = True

    db.commit()
    db.refresh(fase)

    # Log audit
    audit = AuditService(db)
    audit.log_update(
        entity="Fase",
        entity_id=fase.id,
        old_values={"estado": old_estado.value},
        new_values={"estado": estado.value},
    )

    return FaseResponse.model_validate(fase)


@router.post("/fases/{fase_id}/enviar-revision", response_model=FaseResponse)
def enviar_a_revision(fase_id: UUID, db: Session = Depends(get_db)):
    """Send fase to review."""
    fase = get_fase_or_404(db, fase_id)

    if fase.estado not in [EstadoExpediente.BORRADOR, EstadoExpediente.EN_AJUSTE]:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede enviar a revisión desde estado {fase.estado.value}",
        )

    old_estado = fase.estado
    fase.estado = EstadoExpediente.EN_REVISION

    db.commit()
    db.refresh(fase)

    # Log audit
    audit = AuditService(db)
    audit.log_update(
        entity="Fase",
        entity_id=fase.id,
        old_values={"estado": old_estado.value},
        new_values={"estado": EstadoExpediente.EN_REVISION.value},
    )

    return FaseResponse.model_validate(fase)


@router.post("/fases/{fase_id}/aprobar", response_model=FaseResponse)
def aprobar_fase(fase_id: UUID, db: Session = Depends(get_db)):
    """Approve a fase."""
    fase = get_fase_or_404(db, fase_id)

    if fase.estado != EstadoExpediente.EN_REVISION:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden aprobar fases en estado EN_REVISION",
        )

    old_estado = fase.estado
    fase.estado = EstadoExpediente.VALIDADO_TECNICAMENTE
    fase.completada = True

    db.commit()
    db.refresh(fase)

    # Log audit
    audit = AuditService(db)
    audit.log_update(
        entity="Fase",
        entity_id=fase.id,
        old_values={"estado": old_estado.value},
        new_values={"estado": EstadoExpediente.VALIDADO_TECNICAMENTE.value, "completada": True},
    )

    return FaseResponse.model_validate(fase)


@router.put("/fases/{fase_id}/campos/{clave}")
def update_campo(
    fase_id: UUID,
    clave: str,
    valor: str,
    db: Session = Depends(get_db),
):
    """Update or create a campo in a fase."""
    from app.models.campo import Campo

    fase = get_fase_or_404(db, fase_id)

    # Find or create campo
    campo = db.query(Campo).filter(
        Campo.fase_id == fase_id,
        Campo.clave == clave,
    ).first()

    if campo:
        old_valor = campo.valor
        campo.valor = valor
    else:
        campo = Campo(
            fase_id=fase_id,
            clave=clave,
            valor=valor,
        )
        db.add(campo)

    db.commit()
    db.refresh(campo)

    return {"id": str(campo.id), "clave": campo.clave, "valor": campo.valor}


@router.get("/fases/{fase_id}/campos")
def list_campos(fase_id: UUID, db: Session = Depends(get_db)):
    """List all campos for a fase."""
    fase = get_fase_or_404(db, fase_id)
    return [{"id": str(c.id), "clave": c.clave, "valor": c.valor, "tipo": c.tipo} for c in fase.campos]


@router.post("/fases/{fase_id}/auto-fill")
def auto_fill_fase_endpoint(fase_id: UUID, db: Session = Depends(get_db)):
    """Auto-fill fase fields using AI/RAG suggestions."""
    result = auto_fill_fase_sync(str(fase_id), db)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Error"))
    return result


@router.post("/fases/{fase_id}/mejorar-contenido")
async def mejorar_contenido_fase(
    fase_id: UUID,
    clave: str,
    db: Session = Depends(get_db),
):
    """Improve a specific campo's content using AI."""
    from app.models.campo import Campo
    from app.services.audit import AuditService

    fase = get_fase_or_404(db, fase_id)
    campo = db.query(Campo).filter(
        Campo.fase_id == fase_id,
        Campo.clave == clave,
    ).first()

    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")

    # Get fase context
    expediente = fase.expediente
    programa = expediente.nombre_programa if expediente else ""
    contexto = f"Fase: {fase.nombre}\nPrograma: {programa}\nCampo: {clave}\n\nContenido actual:\n{campo.valor}"

    # Improve content using AI
    improved = await mejorar_contenido(campo.valor, contexto)

    # Update campo
    old_valor = campo.valor
    campo.valor = improved

    audit = AuditService(db)
    audit.log_update(
        entity="Campo",
        entity_id=campo.id,
        old_values={"valor": old_valor[:100] + "..."},
        new_values={"valor": improved[:100] + "..."},
    )

    db.commit()

    return {
        "success": True,
        "campo_id": str(campo.id),
        "clave": clave,
        "contenido_anterior": old_valor,
        "contenido_mejorado": improved,
    }


@router.post("/fases/{fase_id}/mejorar-todos")
async def mejorar_todos_campos(
    fase_id: UUID,
    db: Session = Depends(get_db),
):
    """Improve all campos content using AI."""
    from app.models.campo import Campo
    from app.services.audit import AuditService

    fase = get_fase_or_404(db, fase_id)
    expediente = fase.expediente
    programa = expediente.nombre_programa if expediente else ""

    campos = db.query(Campo).filter(Campo.fase_id == fase_id).all()

    results = []
    for campo in campos:
        contexto = f"Fase: {fase.nombre}\nPrograma: {programa}\nCampo: {campo.clave}\n\nContenido actual:\n{campo.valor}"
        improved = await mejorar_contenido(campo.valor, contexto)

        old_valor = campo.valor
        campo.valor = improved

        audit = AuditService(db)
        audit.log_update(
            entity="Campo",
            entity_id=campo.id,
            old_values={"valor": old_valor[:100] + "..."},
            new_values={"valor": improved[:100] + "..."},
        )

        results.append({
            "id": str(campo.id),
            "clave": campo.clave,
            "mejorado": improved != old_valor,
        })

    db.commit()

    return {
        "success": True,
        "fase_id": str(fase_id),
        "fase_nombre": fase.nombre,
        "campos_procesados": len(results),
        "results": results,
    }


@router.post("/expedientes/{expediente_id}/auto-fill-fases")
def auto_fill_all_fases(expediente_id: UUID, db: Session = Depends(get_db)):
    """Auto-fill all fases of an expediente using AI/RAG."""
    result = auto_fill_expediente_fases_sync(str(expediente_id), db)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Error"))
    return result