# Tasks: core-expediente-fases

Implementation order for MVP core expediente and fases.

---

## Phase 1: Project Setup

### Task: Initialize FastAPI backend
- **Step:** Create backend directory structure
- **Step:** Set up Python 3.11+ venv
- **Step:** Install dependencies (FastAPI, SQLAlchemy, Alembic, pg8000, python-jose, python-multipart)
- **Step:** Create initial app structure with config.py
- **Step:** Set up Alembic for migrations
- **Step:** Create .env.example with required variables
- **Verification:** `uvicorn main:app --reload` starts without errors

### Task: Initialize Next.js frontend
- **Step:** Create frontend directory
- **Step:** Initialize Next.js 15 with App Router
- **Step:** Install Tailwind CSS and shadcn/ui
- **Step:** Configure shadcn/ui with custom theme
- **Step:** Set up API client (fetch or RTK Query)
- **Verification:** `npm run dev` shows homepage

---

## Phase 2: Database Model

### Task: Create database schema
- **Step:** Create SQLAlchemy models for all entities
  - `expedientes` table
  - `fases` table
  - `campos` table
  - `evidencias` table
  - `observaciones` table
  - `versiones` table
  - `audit_logs` table
- **Step:** Create enums for estados
- **Step:** Create relationships between models
- **Step:** Add indexes for common queries
- **Verification:** `alembic upgrade head` runs successfully

### Task: Create database migrations
- **Step:** Generate initial migration with alembic
- **Step:** Verify migration creates all tables
- **Step:** Create seed data for phases (10 fases)
- **Verification:** Tables exist and have correct columns

---

## Phase 3: Expediente API

### Task: CRUD Expedientes
- **Step:** Create ExpedienteCreate schema (Pydantic)
- **Step:** Create ExpedienteResponse schema
- **Step:** Implement POST /api/expedientes
- **Step:** Implement GET /api/expedientes (list with filters)
- **Step:** Implement GET /api/expedientes/{id}
- **Step:** Implement PUT /api/expedientes/{id}
- **Step:** Implement DELETE /api/expedientes/{id} (only if BORRADOR)
- **Verification:** All endpoints return correct status codes and data

### Task: Auto-create fases
- **Step:** Create function to auto-create 10 fases
- **Step:** Call auto-create function in expediente creation
- **Step:** Add to database seed/migration
- **Verification:** New expediente has 10 fases

---

## Phase 4: Fase API

### Task: Fase endpoints
- **Step:** Create FaseUpdate schema
- **Step:** Implement GET /api/expedientes/{id}/fases
- **Step:** Implement GET /api/fases/{id}
- **Step:** Implement PUT /api/fases/{id}
- **Step:** Implement PUT /api/fases/{id}/estado
- **Verification:** Fase endpoints work correctly

### Task: Fase state transitions
- **Step:** Implement POST /api/fases/{id}/enviar-revision
- **Step:** Implement POST /api/fases/{id}/aprobar
- **Step:** Add validation for state transitions
- **Step:** Update completada flag on approval
- **Verification:** State machine works correctly

### Task: Campo CRUD
- **Step:** Create Campo schema
- **Step:** Implement GET /api/fases/{id}/campos
- **Step:** Implement PUT /api/fases/{id}/campos/{clave}
- **Verification:** Can store and retrieve field values

---

## Phase 5: Evidence Upload

### Task: File upload service
- **Step:** Create file storage service (local filesystem)
- **Step:** Implement file validation (type, size)
- **Step:** Create unique filenames with UUID
- **Verification:** Files are stored correctly

### Task: Evidence endpoints
- **Step:** Create Evidencia schema
- **Step:** Implement POST /api/fases/{id}/evidencias (multipart upload)
- **Step:** Implement GET /api/fases/{id}/evidencias
- **Step:** Implement GET /api/evidencias/{id}/download
- **Step:** Implement DELETE /api/evidencias/{id}
- **Verification:** Can upload, download, and delete files

---

## Phase 6: Observations

### Task: Observation endpoints
- **Step:** Create Observacion schema
- **Step:** Implement POST /api/fases/{id}/observaciones
- **Step:** Implement GET /api/fases/{id}/observaciones
- **Step:** Implement PUT /api/observaciones/{id}/revisada
- **Verification:** Can create and manage observations

### Task: Observation triggers
- **Step:** Auto-change fase estado on DEVOLUCION
- **Step:** Auto-change fase estado on APROBACION
- **Step:** Create audit log entries
- **Verification:** State changes trigger correctly

---

## Phase 7: Version History

### Task: Version tracking
- **Step:** Create Version schema
- **Step:** Create auto-save on field changes
- **Step:** Implement GET /api/expedientes/{id}/versiones
- **Verification:** Changes create version entries

### Task: Audit log
- **Step:** Create AuditLog middleware/service
- **Step:** Log all CREATE, UPDATE, DELETE actions
- **Step:** Implement GET /api/expedientes/{id}/audit
- **Verification:** All actions are logged

---

## Phase 8: Dashboard

### Task: Dashboard API
- **Step:** Create dashboard summary endpoint
- **Step:** Calculate progress percentage
- **Step:** Identify pending actions
- **Step:** Identify overdue items
- **Verification:** Dashboard shows correct data

### Task: Dashboard frontend
- **Step:** Create Dashboard page component
- **Step:** Display expediente cards/list
- **Step:** Show progress indicators
- **Step:** Show alerts and pending items
- **Verification:** Dashboard renders correctly

---

## Phase 9: Expediente Views

### Task: Create expediente page
- **Step:** Create ExpedienteForm component
- **Step:** Form fields: tipo_tramite, nombre, facultad, nivel, modalidad, lugar
- **Step:** Handle submit and API call
- **Step:** Redirect to expediente view after creation
- **Verification:** Can create new expediente through UI

### Task: Expediente detail view
- **Step:** Create ExpedienteDetail page
- **Step:** Display all fases as tabs or accordion
- **Step:** Show estado and progress
- **Step:** Show recent activity
- **Verification:** Shows expediente with all fases

### Task: Fase form
- **Step:** Create FaseForm component
- **Step:** Display fase fields dynamically
- **Step:** Add evidence upload section
- **Step:** Add observations section
- **Verification:** Can edit fase through UI

### Task: Fase state actions
- **Step:** Add "Enviar a revisión" button
- **Step:** Add "Aprobar" button
- **Step:** Add observation form
- **Verification:** State actions work through UI

---

## Phase 10: History View

### Task: Version history UI
- **Step:** Create History page
- **Step:** List all versions with timestamps
- **Step:** Show diff between versions (optional)
- **Verification:** Shows version history

### Task: Audit log UI
- **Step:** Create AuditLog table component
- **Step:** Filter by action, entity, date
- **Verification:** Shows audit trail

---

## Phase 11: Polish

### Task: Error handling
- **Step:** Add global error handler
- **Step:** Add validation error messages
- **Step:** Add 404 pages
- **Verification:** Error pages are user-friendly

### Task: Loading states
- **Step:** Add loading skeletons
- **Step:** Add progress indicators
- **Verification:** UI shows loading states

### Task: Empty states
- **Step:** Add empty state messages
- **Step:** Add "Create first expediente" CTA
- **Verification:** Empty states are helpful

---

## Completion Criteria

- [x] User can create new expediente (NUEVO/RENOVACION)
- [x] User can see all 10 fases
- [x] User can edit fase fields
- [x] User can upload evidence files
- [x] User can add observations
- [x] User can change fase estado (workflow)
- [ ] User can see dashboard with progress
- [ ] User can see version history
- [x] All actions are logged in audit log