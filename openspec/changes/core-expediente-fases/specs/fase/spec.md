## ADDED Requirements

### Requirement: Create Fases for Expediente
The system SHALL automatically create 10 fases when creating an expediente.

The fases are:
1. Gestión de la Solicitud Académica
2. Análisis de Pertinencia, Identidad Institucional y Oportunidad Formativa
3. Estudio de Viabilidad Institucional, Operativa y Financiera
4. Diseño Curricular y Perfil de Formación
5. Desarrollo de Condiciones de Calidad del Programa
6. Articulación con Condiciones Institucionales de Calidad
7. Verificación Técnica, Normativa y de Coherencia Curricular
8. Gestión de Aprobaciones y Trazabilidad Institucional
9. Generación del Documento Maestro y Evidencias de Soporte
10. Radicación, Seguimiento y Operación Inicial del Programa

#### Scenario: Auto-create fases
- **GIVEN** new expediente is created
- **WHEN** expediente creation completes
- **THEN** system creates 10 fases with numero 1-10
- **AND** all fases have estado=BORRADOR
- **AND** all fases have completada=FALSE

---

### Requirement: Get Fases
The system SHALL return all fases for an expediente ordered by numero.

#### Scenario: List fases
- **GIVEN** expediente with existing fases
- **WHEN** user requests GET /api/expedientes/{id}/fases
- **THEN** system returns 10 fases in order
- **AND** each fase includes: id, numero, nombre, estado, completada, created_at

---

### Requirement: Update Fase State
The system SHALL allow state transitions according to workflow.

#### Scenario: Send fase to revision
- **GIVEN** fase exists with estado=BORRADOR or estado=EN_AJUSTE
- **WHEN** user calls POST /api/fases/{id}/enviar-revision
- **THEN** fase estado changes to EN_REVISION

#### Scenario: Return fase with observations
- **GIVEN** fase exists with estado=EN_REVISION
- **WHEN** reviewer creates observacion with tipo=DEVOLUCION
- **THEN** fase estado changes to CON_OBSERVACIONES

#### Scenario: Approve fase
- **GIVEN** fase exists with estado=EN_REVISION
- **WHEN** authorized reviewer calls POST /api/fases/{id}/aprobar
- **THEN** fase estado changes to VALIDADO_TECNICAMENTE
- **AND** fase completada=TRUE

---

### Requirement: Fase Field Values
The system SHALL store arbitrary key-value fields for each fase.

#### Scenario: Update fase field
- **GIVEN** fase exists
- **WHEN** user updates field with clave="justificacion"
- **THEN** system stores or updates campo record
- **AND** system creates version entry

---

### Requirement: Fase Completion Tracking
The system SHALL track when a fase is completed.

#### Scenario: Mark fase as completed
- **WHEN** fase reaches VALIDADO_TECNICAMENTE or higher
- **THEN** fase completada=TRUE
- **AND** fase.updated_at is updated

#### Scenario: Reopen fase
- **WHEN** approved fase receives new observacion
- **THEN** fase completada=FALSE
- **AND** fase estado changes to CON_OBSERVACIONES or EN_AJUSTE