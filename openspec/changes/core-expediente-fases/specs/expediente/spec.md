## ADDED Requirements

### Requirement: Create Academic Program Expediente
The system SHALL allow users with LÍDER_DE_PROPUESTA role to create a new expediente for either a new program or a registration renewal.

#### Scenario: Create new program expediente
- **GIVEN** user is authenticated with LÍDER_DE_PROPUESTA role
- **WHEN** user submits create expediente form with tipo_tramite="NUEVO"
- **THEN** system creates expediente with estado=BORRADOR
- **AND** system creates 10 empty fases associated to the expediente
- **AND** system returns the created expediente with all fases

#### Scenario: Create renewal expediente
- **GIVEN** user is authenticated with LÍDER_DE_PROPUESTA role
- **WHEN** user submits create expediente form with tipo_tramite="RENOVACION"
- **THEN** system creates expediente with tipo_tramite="RENOVACION" and estado=BORRADOR
- **AND** system creates 10 empty fases

---

### Requirement: Expediente Data Fields
The system SHALL require the following fields when creating an expediente:
- tipo_tramite: NUEVO | RENOVACION (required)
- nombre_programa: string (required)
- facultad: string (optional)
- nivel: string (optional)
- modalidad: string (optional)
- lugar_desarrollo: string (optional)
- responsable_id: UUID (optional, defaults to current user)

---

### Requirement: List Expedientes
The system SHALL return a paginated list of expedientes with filters.

#### Scenario: List all expedientes
- **GIVEN** user is authenticated
- **WHEN** user requests GET /api/expedientes
- **THEN** system returns list of expedientes user has access to
- **AND** results include: id, nombre_programa, tipo_tramite, estado, created_at, updated_at

#### Scenario: Filter by estado
- **GIVEN** user is authenticated
- **WHEN** user requests GET /api/expedientes?estado=EN_FORMULACION
- **THEN** system returns only expedientes in EN_FORMULACION estado

#### Scenario: Filter by tipo_tramite
- **GIVEN** user is authenticated
- **WHEN** user requests GET /api/expedientes?tipo_tramite=NUEVO
- **THEN** system returns only nuevos programas

---

### Requirement: Update Expediente
The system SHALL allow updating expediente fields only if estado allows editing.

#### Scenario: Update expediente in BORRADOR
- **GIVEN** expediente exists with estado=BORRADOR
- **WHEN** user with proper role updates expediente fields
- **THEN** system updates fields
- **AND** system creates version entry

#### Scenario: Update expediente not in BORRADOR
- **GIVEN** expediente exists with estado=EN_REVISION
- **WHEN** user tries to update expediente fields
- **THEN** system returns 403 Forbidden

---

### Requirement: Expediente State Transitions
The system SHALL track estado changes and create audit log entries.

#### Scenario: Change estado
- **WHEN** expediente estado changes from one state to another
- **THEN** system updates estado field
- **AND** system creates audit_log entry with action=UPDATE, entity=Expediente, old_values, new_values