"""Evidencias router."""
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Evidencia, Fase
from app.models.enums import EstadoExpediente
from app.schemas.evidencia import EvidenciaResponse
from app.services.storage import StorageService
from app.services.audit import AuditService
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["evidencias"])


def get_fase_or_404(db: Session, fase_id: UUID) -> Fase:
    """Helper to get fase or raise 404."""
    fase = db.query(Fase).filter(Fase.id == fase_id).first()
    if not fase:
        raise HTTPException(status_code=404, detail="Fase no encontrada")
    return fase


@router.post("/fases/{fase_id}/evidencias", response_model=EvidenciaResponse)
async def upload_evidencia(
    fase_id: UUID,
    file: UploadFile = File(...),
    campo_id: UUID | None = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a file as evidence for a fase."""
    fase = get_fase_or_404(db, fase_id)

    # Check fase allows editing
    if fase.estado not in [EstadoExpediente.BORRADOR, EstadoExpediente.EN_AJUSTE]:
        raise HTTPException(
            status_code=403,
            detail="No se pueden subir evidencias a fases en este estado",
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file
    storage = StorageService()
    is_valid, error_msg = storage.validate_file(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Save file
    storage_path, original_name = storage.save_file(
        content,
        file.filename,
    )

    # Create evidencia record
    evidencia = Evidencia(
        fase_id=fase_id,
        campo_id=campo_id,
        nombre_archivo=original_name,
        ruta_storage=storage_path,
        tipo_mime=storage.get_mime_type(original_name),
        tamano_bytes=file_size,
    )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)

    # Log audit
    audit = AuditService(db)
    audit.log_create(
        entity="Evidencia",
        entity_id=evidencia.id,
        new_values={"nombre_archivo": original_name},
    )

    response = EvidenciaResponse.model_validate(evidencia)
    settings = get_settings()
    response.download_url = f"/api/evidencias/{evidencia.id}/download"
    return response


@router.get("/fases/{fase_id}/evidencias", response_model=list[EvidenciaResponse])
def list_evidencias(fase_id: UUID, db: Session = Depends(get_db)):
    """List all evidencias for a fase."""
    fase = get_fase_or_404(db, fase_id)

    evidencias = db.query(Evidencia).filter(Evidencia.fase_id == fase_id).all()

    result = []
    for ev in evidencias:
        resp = EvidenciaResponse.model_validate(ev)
        resp.download_url = f"/api/evidencias/{ev.id}/download"
        result.append(resp)

    return result


@router.get("/evidencias/{evidencia_id}/download")
def download_evidencia(evidencia_id: UUID, db: Session = Depends(get_db)):
    """Download an evidencia file."""
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id).first()

    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")

    file_path = Path(evidencia.ruta_storage)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")

    return FileResponse(
        path=str(file_path),
        filename=evidencia.nombre_archivo,
        media_type=evidencia.tipo_mime,
    )


@router.delete("/evidencias/{evidencia_id}", status_code=204)
def delete_evidencia(evidencia_id: UUID, db: Session = Depends(get_db)):
    """Delete an evidencia."""
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id).first()

    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")

    # Check fase allows editing
    fase = db.query(Fase).filter(Fase.id == evidencia.fase_id).first()
    if fase and fase.estado not in [EstadoExpediente.BORRADOR, EstadoExpediente.EN_AJUSTE]:
        raise HTTPException(
            status_code=403,
            detail="No se pueden eliminar evidencias en este estado",
        )

    old_values = {"nombre_archivo": evidencia.nombre_archivo}

    # Delete file
    storage = StorageService()
    storage.delete_file(evidencia.ruta_storage)

    # Log audit before delete
    audit = AuditService(db)
    audit.log_delete(
        entity="Evidencia",
        entity_id=evidencia.id,
        old_values=old_values,
    )

    db.delete(evidencia)
    db.commit()