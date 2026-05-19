## ADDED Requirements

### Requirement: Dashboard Overview
The system SHALL show a dashboard with all active expedientes and their status.

#### Scenario: View dashboard
- **GIVEN** user is authenticated
- **WHEN** user navigates to / or /expedientes
- **THEN** system displays list of expedientes user has access to
- **AND** each row shows: nombre_programa, tipo_tramite, estado, avance (%), última actividad

---

### Requirement: Expediente Progress Calculation
The system SHALL calculate progress percentage based on completed fases.

#### Scenario: Calculate progress
- **GIVEN** expediente has 10 fases
- **AND** 4 fases have completada=TRUE
- **WHEN** progress is calculated
- **THEN** progress = 40%

---

### Requirement: Risk Indicators
The system SHALL show risk indicators on the dashboard.

#### Scenario: Show risk indicators
- **GIVEN** expediente exists
- **WHEN** calculating risk indicators
- **THEN** system shows:
  - Fases overdue (past expected completion date)
  - Fases with unresolved observations
  - High number of revisions

---

### Requirement: Expediente Board View
The system SHALL provide a Kanban-style board view grouped by estado.

#### Scenario: Board view
- **GIVEN** user requests /expedientes/board
- **WHEN** system renders board
- **THEN** system groups expedientes by estado
- **AND** each column shows count and expediente cards

---

### Requirement: Alerts and Notifications
The system SHALL show alerts for:
- Expedientes pending user action
- Fases approaching deadline
- New observations to review

#### Scenario: Show alerts
- **GIVEN** user has pending observations
- **WHEN** dashboard loads
- **THEN** system shows alert badge with count
- **AND** clicking shows list of items requiring attention

---

### Requirement: Quick Actions
The system SHALL provide quick actions from dashboard:
- Create new expediente
- View my expedientes
- View pending revisions
- View recent activity