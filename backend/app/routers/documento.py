"""Documento maestro router."""
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Expediente, Fase, Evidencia, Observacion, Version
from app.models.enums import EstadoExpediente
from app.services.audit import AuditService

router = APIRouter(prefix="/api", tags=["documento"])

# Nombres oficiales de las 10 fases
FASES_NOMBRES = [
    "Gestión de la Solicitud Académica",
    "Análisis de Pertinencia, Identidad Institucional y Oportunidad Formativa",
    "Estudio de Viabilidad Institucional, Operativa y Financiera",
    "Diseño Curricular y Perfil de Formación",
    "Desarrollo de Condiciones de Calidad del Programa",
    "Articulación con Condiciones Institucionales de Calidad",
    "Verificación Técnica, Normativa y de Coherencia Curricular",
    "Gestión de Aprobaciones y Trazabilidad Institucional",
    "Generación del Documento Maestro y Evidencias de Soporte",
    "Radicación, Seguimiento y Operación Inicial del Programa",
]

ESTADO_LABELS = {
    EstadoExpediente.BORRADOR: "Borrador",
    EstadoExpediente.EN_FORMULACION: "En Formulación",
    EstadoExpediente.EN_REVISION: "En Revisión",
    EstadoExpediente.CON_OBSERVACIONES: "Con Observaciones",
    EstadoExpediente.EN_AJUSTE: "En Ajuste",
    EstadoExpediente.VALIDADO_TECNICAMENTE: "Validado Técnicamente",
    EstadoExpediente.PENDIENTE_APROBACION: "Pendiente Aprobación",
    EstadoExpediente.APROBADO: "Aprobado",
    EstadoExpediente.DOCUMENTO_GENERADO: "Documento Generado",
    EstadoExpediente.RADICADO: "Radicado",
    EstadoExpediente.EN_SEGUIMIENTO: "En Seguimiento",
    EstadoExpediente.CERRADO: "Cerrado",
}


@router.post("/expedientes/{expediente_id}/generar-documento")
def generar_documento_maestro(expediente_id: UUID, db: Session = Depends(get_db)):
    """Genera el documento maestro del expediente."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    # Verificar que todas las fases estén completadas
    fases = db.query(Fase).filter(
        Fase.expediente_id == expediente_id
    ).order_by(Fase.numero).all()

    if len(fases) != 10:
        raise HTTPException(
            status_code=400,
            detail="El expediente debe tener las 10 fases registradas",
        )

    fases_pendientes = [f for f in fases if not f.completada]
    if fases_pendientes:
        raise HTTPException(
            status_code=400,
            detail=f"El expediente tiene {len(fases_pendientes)} fases pendientes de completar antes de generar el documento maestro",
        )

    # Recopilar evidencias
    evidencias_por_fase = []
    for fase in fases:
        evs = db.query(Evidencia).filter(Evidencia.fase_id == fase.id).all()
        evidencias_por_fase.append({
            "fase_numero": fase.numero,
            "fase_nombre": FASES_NOMBRES[fase.numero - 1] if fase.numero <= 10 else "",
            "estado": ESTADO_LABELS.get(fase.estado, fase.estado.value),
            "evidencias": [
                {
                    "nombre": e.nombre_archivo,
                    "tipo": e.tipo,
                    "fecha": e.created_at.isoformat() if e.created_at else None,
                }
                for e in evs
            ],
            "num_evidencias": len(evs),
        })

    # Recopilar observaciones clave
    observaciones = db.query(Observacion).join(
        Fase, Observacion.fase_id == Fase.id
    ).filter(
        Fase.expediente_id == expediente_id
    ).order_by(Observacion.created_at.desc()).limit(20).all()

    # Contar versiones
    versiones_count = db.query(Version).filter(
        Version.expediente_id == expediente_id
    ).count()

    # Calcular estadísticas
    total_evidencias = sum(e["num_evidencias"] for e in evidencias_por_fase)
    total_observaciones = len(observaciones)

    # Construir documento maestro
    documento = {
        "meta": {
            "titulo": f"Documento Maestro - {expediente.nombre_programa}",
            "tipo_tramite": expediente.tipo_tramite.value if hasattr(expediente.tipo_tramite, 'value') else expediente.tipo_tramite,
            "fecha_generacion": datetime.utcnow().isoformat(),
            "version": versiones_count + 1,
        },
        "informacion_general": {
            "programa": expediente.nombre_programa,
            "facultad": expediente.facultad or "No especificada",
            "nivel": expediente.nivel or "No especificado",
            "modalidad": expediente.modalidad or "No especificada",
            "lugar": expediente.lugar_desarrollo or "No especificado",
        },
        "resumen_ejecutivo": {
            "total_fases": 10,
            "fases_completadas": len([f for f in fases if f.completada]),
            "total_evidencias": total_evidencias,
            "total_observaciones": total_observaciones,
            "progreso": expediente.progreso,
            "estado_general": ESTADO_LABELS.get(expediente.estado, expediente.estado.value),
        },
        "fases": evidencias_por_fase,
        "observaciones_recientes": [
            {
                "fase": FASES_NOMBRES[obs.fase_id - 1] if obs.fase_id and obs.fase_id <= 10 else "General",
                "contenido": obs.contenido,
                "autor": obs.autor,
                "fecha": obs.created_at.isoformat() if obs.created_at else None,
                "tipo": obs.tipo.value if hasattr(obs.tipo, 'value') else "OBSERVACION",
            }
            for obs in observaciones
        ],
        "trazabilidad": {
            "created_at": expediente.created_at.isoformat() if expediente.created_at else None,
            "updated_at": expediente.updated_at.isoformat() if expediente.updated_at else None,
            "numero_versiones": versiones_count,
        },
    }

    # Log audit
    audit = AuditService(db)
    audit.log_create(
        entity="DocumentoMaestro",
        entity_id=expediente_id,
        new_values={"fases": 10, "evidencias": total_evidencias},
    )

    return {
        "success": True,
        "documento": documento,
        "mensaje": "Documento maestro generado exitosamente",
    }


@router.get("/expedientes/{expediente_id}/documento-preview")
def get_documento_preview(expediente_id: UUID, db: Session = Depends(get_db)):
    """Preview del documento maestro sin generar."""
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    fases = db.query(Fase).filter(
        Fase.expediente_id == expediente_id
    ).order_by(Fase.numero).all()

    # Calcular progreso dinámicamente
    fases_completadas = len([f for f in fases if f.completada])
    progreso = int((fases_completadas / 10) * 100) if fases else 0

    # Estadísticas
    total_evidencias = db.query(Evidencia).join(Fase).filter(
        Fase.expediente_id == expediente_id
    ).count()

    return {
        "programa": expediente.nombre_programa,
        "fases_registradas": len(fases),
        "fases_completadas": fases_completadas,
        "fases_pendientes": len([f for f in fases if not f.completada]),
        "total_evidencias": total_evidencias,
        "progreso": progreso,
        "estado": expediente.estado.value if hasattr(expediente.estado, 'value') else expediente.estado,
        "listo_para_generar": len(fases) == 10 and all(f.completada for f in fases),
        "mensaje": "Documento listo para generar" if len(fases) == 10 and all(f.completada for f in fases) else "Completar fases pendientes primero",
    }