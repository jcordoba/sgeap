## ADDED Requirements

### Requirement: Create Observation
The system SHALL allow reviewers to create observations on a fase.

#### Scenario: Create general observation
- **GIVEN** fase exists
- **WHEN** reviewer creates observation with tipo=OBSERVACION
- **THEN** system creates observacion record
- **AND** sistema notifies relevant users

#### Scenario: Return fase for adjustments
- **GIVEN** fase exists with estado=EN_REVISION
- **WHEN** reviewer creates observation with tipo=DEVOLUCION
- **THEN** observacion tipo=DEVOLUCION
- **AND** fase estado changes to CON_OBSERVACIONES

---

### Requirement: Observation Types
The system SHALL support these observation types:
- OBSERVACION: general comment or suggestion
- DEVOLUCION: fase returned for corrections
- APROBACION: fase approved (also triggers estado change)

---

### Requirement: List Observations
The system SHALL return all observations for a fase, ordered by created_at.

#### Scenario: List fase observations
- **GIVEN** fase has observations
- **WHEN** user requests GET /api/fases/{id}/observaciones
- **THEN** system returns list with: id, autor, tipo, contenido, revisada, created_at

---

### Requirement: Mark Observation as Reviewed
The system SHALL allow users to mark observations as reviewed.

#### Scenario: Mark observation as reviewed
- **GIVEN** observacion exists with revisada=FALSE
- **WHEN** user who received observation marks it as revisada
- **THEN** observacion revisada=TRUE
- **AND** observacion.updated_at is updated

---

### Requirement: Observation Notifications
The system SHALL notify relevant users when an observation is created.

For DEVOLUCION type:
- Notify: LÍDER_DE_PROPUESTA, assigned EQUIPO_ACADÉMICO

For OBSERVACION type:
- Notify: LÍDER_DE_PROPUESTA

(Email/notification system comes in future change)