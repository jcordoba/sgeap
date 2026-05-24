"""AI service for auto-filling phases using RAG + MiniMax."""
import asyncio
from typing import Optional

from sqlalchemy import create_engine, text

from app.models import Fase, Campo
from app.models.enums import EstadoExpediente
from app.config import get_settings

settings = get_settings()

RAG_DB_URL = "postgresql+pg8000://rag_user:rag_pass_2026@localhost:5434/sgeap_rag"
rag_engine = create_engine(RAG_DB_URL)


async def generar_campos_fase_ai(fase: Fase, expediente_programa: str = "") -> dict[str, str]:
    """Generate phase fields using MiniMax AI + RAG context."""
    from app.services.ai_minimax import generar_contenido_fase

    fase_nombre = fase.nombre

    # First get RAG context for relevant documents
    rag_docs = await obtener_contexto_rag(fase_nombre, expediente_programa)

    # Build context for AI
    contexto = ""
    if rag_docs:
        contexto = f"Documentos institucionales de referencia:\n{rag_docs}"

    # Generate content using MiniMax
    try:
        campos = await generar_contenido_fase(
            fase_nombre=fase_nombre,
            programa_nombre=expediente_programa,
            contexto_adicional=contexto
        )
        return campos
    except Exception as e:
        print(f"MiniMax generation error: {e}")
        return generar_campos_fallback(fase_nombre)


async def obtener_contexto_rag(fase_nombre: str, programa: str = "", max_docs: int = 2) -> str:
    """Get RAG context for additional information."""
    try:
        from app.services.embedding import generate_embedding, vector_to_sql

        query = f"{fase_nombre}"
        if programa:
            query += f" {programa}"

        query_embedding = generate_embedding(query)
        query_vector = vector_to_sql(query_embedding)

        with rag_engine.connect() as conn:
            sql = text("""
                SELECT titulo, contenido_resumido
                FROM documentos_rag_embeddings
                WHERE vigente = TRUE
                ORDER BY embedding <=> CAST(:query_vector AS vector)
                LIMIT :max_docs
            """)
            result = conn.execute(sql, {"query_vector": query_vector, "max_docs": max_docs})
            rows = result.fetchall()

            context_parts = []
            for row in rows:
                if row[1]:
                    context_parts.append(f"- {row[0]}: {row[1][:300]}...")
                else:
                    context_parts.append(f"- {row[0]}")

            return "\n".join(context_parts) if context_parts else ""

    except Exception as e:
        print(f"RAG context error: {e}")
        return ""


def generar_campos_fallback(fase_nombre: str) -> dict[str, str]:
    """Generate fallback template when AI fails."""
    templates = {
        "Información General del Programa": {
            "introduccion": "Esta fase establece la información básica del programa académico incluyendo datos de identificación,Snaturaleza jurídica y características institucionales.",
            "objetivos": "1. Identificar datos generales del programa\n2. DefinirSnaturaleza y alcance\n3. EstablecerSnormativa aplicable",
            "requisitos": "- Nombre completo del programa\n- Código SNP\n- Facultad responsable\n- Modalidad de formación",
            "recomendaciones": "Consulte la normativa institucional vigente para correctamente los campos."
        },
        "Justificación": {
            "introduccion": "La justificación presenta los argumentos académicos, sociales y técnicos que fundamentan la necesidad de crear el programaSnacadémico.",
            "objetivos": "1. Demostrar la necesidad social del programa\n2. Justificar la demanda laboral\n3. Articular con lineamientos institucionales",
            "requisitos": "- Estudio de necesidades sociales\n- Análisis de demanda laboral\n- Convenios de apoyo (si aplica)",
            "recomendaciones": "Use datos actualizados y fuentes verificables para respaldar los argumentos."
        },
        "Currículo": {
            "introduccion": "El diseño curricular define la estructuraSpedagógica, componentes formativos y estrategias de enseñanza para lograr el perfil de egreso.",
            "objetivos": "1. Definir perfil de egreso\n2. Diseñar estructura curricular\n3. Establecer estrategias pedagógicas\n4. Planificar sistema de evaluación",
            "requisitos": "- Perfil de egreso detallado\n- Distribución de créditos\n- Componentes curriculares\n- Resultados de aprendizaje",
            "recomendaciones": "Alinéese con el modelo pedagógico institucional y estándares de acreditación."
        },
        "Proyecto Educativo Institucional": {
            "introduccion": "El PEI vincula el programa con la misión, visión y principios institucionales que guían la formaciónSnacadémica.",
            "objetivos": "1. Vincular con misión y visión institucional\n2. Definir principios formativos\n3. Articular el modelo pedagógico",
            "requisitos": "- Misión y visión del programa\n- Principios institucionales\n- Modelo pedagógico\n- Valores formativos",
            "recomendaciones": "Revise el Proyecto Educativo Institucional (PEI) de la UNAC paraSncoherencia."
        },
        "Investigación": {
            "introduccion": "Esta fase define las líneas de investigación, semilleros y producción intelectual del programaSnacadémico.",
            "objetivos": "1. Definir líneas de investigación\n2. Planificar semilleros\n3. Proyectar producción intelectual\n4. Establecer redes de investigación",
            "requisitos": "- Líneas de investigación vigentes\n- Plan de semilleros\n- Proyección de publicaciones\n- Convenios de investigación",
            "recomendaciones": "Consulte los grupos de investigación institucionales para alianzas."
        },
        "Extensión": {
            "introduccion": "La extensión define la proyección social, prácticas y convenios del programa con el sector externo.",
            "objetivos": "1. Diseñar proyección social\n2. Definir modelo de prácticas\n3. Establecer convenios\n4. Planificar extensión comunitaria",
            "requisitos": "- Modelo de proyección social\n- Convenios con entidades externas\n- Modelo de prácticas profesionales\n- Proyección a la comunidad",
            "recomendaciones": "Identifique organizaciones aliadas potenciales para convenios de práctica."
        },
        "Docentes": {
            "introduccion": "Esta fase establece el perfil docente, plan de formación ynumero de profesores requeridos.",
            "objetivos": "1. Definir perfil docente\n2. Planificar formación continua\n3. Estimar numero de docentes\n4. Diseñar incentivos académicos",
            "requisitos": "- Perfil docente requerido\n- Plan de formación continua\n- Número estimado de docentes\n- Políticas de dedicación",
            "recomendaciones": "Considere el Estatuto Profesoral y políticas de bienestar docente."
        },
        "Infraestructura": {
            "introduccion": "La infraestructura define los espacios físicos, equipamiento y recursos tecnológicos necesarios.",
            "objetivos": "1. Describir espacios requeridos\n2. Especificar equipamiento\n3. Planificar recursos tecnológicos\n4. Evaluar accesibilidad",
            "requisitos": "- Descripción de espacios físicos\n- Equipamiento especializado\n- Recursos tecnológicos\n- Accesibilidad",
            "recomendaciones": "Consulte el Plan de Desarrollo Institucional para alineación con infraestructura existente."
        },
        "Recursos Financieros": {
            "introduccion": "Esta fase presenta el presupuesto, fuentes de financiación y sostenibilidad financiera del programa.",
            "objetivos": "1. Elaborar presupuesto\n2. Identificar fuentes de financiación\n3. Planificar sostenibilidad\n4. Analizar viabilidad financiera",
            "requisitos": "- Presupuesto detallado\n- Fuentes de financiación\n- Proyección de ingresos\n- Plan de sostenibilidad",
            "recomendaciones": "Utilice formatos institucionales de presupuesto y consulte con финансов."
        },
        "Autoevaluación": {
            "introduccion": "La autoevaluación identifica fortalezas, debilidades y plan de mejora para garantizar la calidadSnacadémica.",
            "objetivos": "1. Evaluar criterios de acreditación\n2. Identificar fortalezas\n3. Reconocer debilidades\n4. Elaborar plan de mejora",
            "requisitos": "- Análisis de criterios\n- Matriz de fortalezas/debilidades\n- Plan de mejora\n- Cronograma de implementación",
            "recomendaciones": "Use los formatos de autoevaluación del CNA para garantizar cobertura de criterios."
        },
    }

    # Find matching template
    fase_lower = fase_nombre.lower()
    for key, campos in templates.items():
        if any(word in fase_lower for word in key.lower().split()):
            return campos

    # Generic template
    return {
        "introduccion": f"Esta fase corresponde a {fase_nombre}. Desarrolle el contenido sesuai con los requisitos institucionales.",
        "objetivos": f"1. Analizar requisitos de {fase_nombre}\n2. Documentar elementos necesarios\n3. Preparar evidencias",
        "requisitos": "- Contenido sesuai con normativa\n- Evidencias de soporte\n- Validación institucional",
        "recomendaciones": "Consulte documentos institucionales y formatos de calidad."
    }


async def auto_fill_fase_ai(fase_id: str, db) -> dict[str, any]:
    """Auto-fill a phase with AI-generated content using MiniMax."""
    from app.services.audit import AuditService

    fase = db.query(Fase).filter(Fase.id == fase_id).first()
    if not fase:
        return {"success": False, "error": "Fase no encontrada"}

    expediente = fase.expediente
    programa_nombre = expediente.nombre_programa if expediente else ""

    # Generate fields using AI
    campos = await generar_campos_fase_ai(fase, programa_nombre)

    audit = AuditService(db)
    created_campos = []

    for clave, valor in campos.items():
        existing = db.query(Campo).filter(
            Campo.fase_id == fase.id,
            Campo.clave == clave,
        ).first()

        if existing:
            old_valor = existing.valor
            existing.valor = valor
            audit.log_update(
                entity="Campo",
                entity_id=existing.id,
                old_values={"valor": old_valor[:50] + "..."},
                new_values={"valor": valor[:50] + "..."},
            )
        else:
            new_campo = Campo(
                fase_id=fase.id,
                clave=clave,
                valor=valor,
                tipo="text",
            )
            db.add(new_campo)
            db.flush()
            created_campos.append({"id": str(new_campo.id), "clave": clave})
            audit.log_create(
                entity="Campo",
                entity_id=new_campo.id,
                new_values={"clave": clave, "valor": valor[:50] + "..."},
            )

    db.commit()

    return {
        "success": True,
        "fase_id": str(fase.id),
        "fase_nombre": fase.nombre,
        "campos_creados": len(created_campos),
        "campos_actualizados": len(campos) - len(created_campos),
        "usada_ia": True,
    }


async def auto_fill_expediente_fases_ai(expediente_id: str, db) -> dict[str, any]:
    """Auto-fill all phases of an expediente using MiniMax AI."""
    from app.services.audit import AuditService

    fases = db.query(Fase).filter(Fase.expediente_id == expediente_id).all()

    if not fases:
        return {"success": False, "error": "Expediente no encontrado"}

    expediente = fases[0].expediente
    programa_nombre = expediente.nombre_programa if expediente else ""

    results = []
    for fase in fases:
        campos = await generar_campos_fase_ai(fase, programa_nombre)
        created = 0

        for clave, valor in campos.items():
            existing = db.query(Campo).filter(
                Campo.fase_id == fase.id,
                Campo.clave == clave,
            ).first()

            if not existing:
                new_campo = Campo(
                    fase_id=fase.id,
                    clave=clave,
                    valor=valor,
                    tipo="text",
                )
                db.add(new_campo)
                created += 1

        results.append({
            "fase_id": str(fase.id),
            "fase_nombre": fase.nombre,
            "campos_creados": created,
        })

    db.commit()

    return {
        "success": True,
        "fases_procesadas": len(fases),
        "usada_ia": True,
        "results": results,
    }


# Sync wrapper for endpoints
def auto_fill_fase_sync(fase_id: str, db) -> dict[str, any]:
    """Synchronous wrapper for auto_fill_fase_ai."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(auto_fill_fase_ai(fase_id, db))
    finally:
        loop.close()


def auto_fill_expediente_fases_sync(expediente_id: str, db) -> dict[str, any]:
    """Synchronous wrapper for auto_fill_expediente_fases_ai."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(auto_fill_expediente_fases_ai(expediente_id, db))
    finally:
        loop.close()