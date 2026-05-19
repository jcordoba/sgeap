"""Enums and constants for estados."""
from enum import Enum


class EstadoExpediente(str, Enum):
    """Estados del expediente."""
    BORRADOR = "BORRADOR"
    EN_FORMULACION = "EN_FORMULACION"
    EN_REVISION = "EN_REVISION"
    CON_OBSERVACIONES = "CON_OBSERVACIONES"
    EN_AJUSTE = "EN_AJUSTE"
    VALIDADO_TECNICAMENTE = "VALIDADO_TECNICAMENTE"
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    APROBADO = "APROBADO"
    DOCUMENTO_GENERADO = "DOCUMENTO_GENERADO"
    RADICADO = "RADICADO"
    EN_SEGUIMIENTO = "EN_SEGUIMIENTO"
    CERRADO = "CERRADO"


class TipoTramite(str, Enum):
    """Tipos de trámite."""
    NUEVO = "NUEVO"
    RENOVACION = "RENOVACION"


class TipoObservacion(str, Enum):
    """Tipos de observación."""
    OBSERVACION = "OBSERVACION"
    DEVOLUCION = "DEVOLUCION"
    APROBACION = "APROBACION"


class ActionType(str, Enum):
    """Tipos de acción para audit log."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# Nombres de las 10 fases institucionales
FASES_INSTITUCIONALES = [
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