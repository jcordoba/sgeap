# Design: core-expediente-fases

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Tablero  │  │ Expediente│  │ Formulario│  │ Historial│   │
│  │          │  │          │  │  de fase  │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Expediente│  │   Fase   │  │ Evidencia│  │  Audit   │   │
│  │  Router  │  │  Router  │  │  Router  │  │  Router  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         DATABASE                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PostgreSQL + pgvector                               │   │
│  │  - expedientes                                       │   │
│  │  - fases                                            │   │
│  │  - campos                                           │   │
│  │  - evidencias                                       │   │
│  │  - observaciones                                    │   │
│  │  - versiones                                       │   │
│  │  - audit_logs                                      │   │
│  │  - users                                           │   │
│  │  - roles                                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### Entidad: Expediente
```sql
CREATE TABLE expedientes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tipo_tramite VARCHAR(20) NOT NULL CHECK (tipo_tramite IN ('NUEVO', 'RENOVACION')),
  nombre_programa VARCHAR(255) NOT NULL,
  facultad VARCHAR(255),
  nivel VARCHAR(50),
  modalidad VARCHAR(100),
  lugar_desarrollo VARCHAR(255),
  responsable_id UUID REFERENCES users(id),
  estado VARCHAR(50) DEFAULT 'BORRADOR',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Entidad: Fase
```sql
CREATE TABLE fases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id UUID REFERENCES expedientes(id) ON DELETE CASCADE,
  numero INTEGER NOT NULL CHECK (numero BETWEEN 1 AND 10),
  nombre VARCHAR(255) NOT NULL,
  estado VARCHAR(50) DEFAULT 'BORRADOR',
  completada BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(expediente_id, numero)
);
```

### Entidad: Campo (contenido por fase)
```sql
CREATE TABLE campos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fase_id UUID REFERENCES fases(id) ON DELETE CASCADE,
  clave VARCHAR(100) NOT NULL,
  valor TEXT,
  tipo VARCHAR(50) DEFAULT 'TEXT', -- TEXT, TEXTAREA, TABLE, NUMBER
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(fase_id, clave)
);
```

### Entidad: Evidencia
```sql
CREATE TABLE evidencias (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fase_id UUID REFERENCES fases(id) ON DELETE CASCADE,
  campo_id UUID REFERENCES campos(id) ON DELETE SET NULL,
  nombre_archivo VARCHAR(255) NOT NULL,
  ruta_storage VARCHAR(500) NOT NULL,
  tipo_mime VARCHAR(100),
  tamano_bytes BIGINT,
  uploaded_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Entidad: Observacion
```sql
CREATE TABLE observaciones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fase_id UUID REFERENCES fases(id) ON DELETE CASCADE,
  autor_id UUID REFERENCES users(id),
  tipo VARCHAR(20) CHECK (tipo IN ('OBSERVACION', 'DEVOLUCION', 'APROBACION')),
  contenido TEXT NOT NULL,
  revisada BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Entidad: Version
```sql
CREATE TABLE versiones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id UUID REFERENCES expedientes(id) ON DELETE CASCADE,
  numero INTEGER NOT NULL,
  fase_id UUID REFERENCES fases(id) ON DELETE SET NULL,
  cambios JSONB NOT NULL,
  creado_por UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(expediente_id, numero)
);
```

### Entidad: AuditLog
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  action VARCHAR(20) CHECK (action IN ('CREATE', 'UPDATE', 'DELETE')),
  entity VARCHAR(50) NOT NULL,
  entity_id UUID,
  old_values JSONB,
  new_values JSONB,
  ip_address INET,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Estados (enum-like)
```sql
CREATE TYPE estado_expediente AS ENUM (
  'BORRADOR',
  'EN_FORMULACION',
  'EN_REVISION',
  'CON_OBSERVACIONES',
  'EN_AJUSTE',
  'VALIDADO_TECNICAMENTE',
  'PENDIENTE_APROBACION',
  'APROBADO',
  'DOCUMENTO_GENERADO',
  'RADICADO',
  'EN_SEGUIMIENTO',
  'CERRADO'
);
```

## API Endpoints

### Expedientes
```
POST   /api/expedientes              # Crear expediente
GET    /api/expedientes              # Listar expedientes
GET    /api/expedientes/{id}         # Obtener expediente
PUT    /api/expedientes/{id}         # Actualizar expediente
DELETE /api/expedientes/{id}         # Eliminar (solo si BORRADOR)
GET    /api/expedientes/{id}/tablero  # Tablero de control
```

### Fases
```
GET    /api/expedientes/{id}/fases   # Listar fases del expediente
GET    /api/fases/{id}               # Obtener fase
PUT    /api/fases/{id}               # Actualizar fase
PUT    /api/fases/{id}/estado         # Cambiar estado de fase
POST   /api/fases/{id}/enviar-revision  # Enviar a revisión
POST   /api/fases/{id}/aprobar       # Aprobar fase
```

### Campos
```
GET    /api/fases/{id}/campos        # Listar campos
PUT    /api/fases/{id}/campos/{clave} # Actualizar campo
```

### Evidencias
```
POST   /api/fases/{id}/evidencias    # Subir evidencia
GET    /api/fases/{id}/evidencias    # Listar evidencias
DELETE /api/evidencias/{id}          # Eliminar evidencia
GET    /api/evidencias/{id}/download # Descargar evidencia
```

### Observaciones
```
POST   /api/fases/{id}/observaciones # Crear observación
GET    /api/fases/{id}/observaciones # Listar observaciones
PUT    /api/observaciones/{id}/revisada # Marcar como revisada
```

### Historial
```
GET    /api/expedientes/{id}/versiones    # Listar versiones
GET    /api/expedientes/{id}/audit        # Audit log
```

## Flujo de Estados

```
                    ┌─────────────┐
                    │  BORRADOR   │
                    └──────┬──────┘
                           │ crear/editar
                           ▼
                    ┌─────────────┐
          ┌─────────│EN_FORMULACION│─────────┐
          │         └──────┬──────┘         │
          │                │ enviar a revisión
          │                ▼
          │         ┌─────────────┐
          │         │EN_REVISION │
          │         └──────┬──────┘
          │         ┌─────┴─────┐
          │         ▼           ▼
          │  ┌──────────┐  ┌──────────────┐
          │  │CON_OBSER │  │VALIDADO_TEC │
          │  └────┬─────┘  └──────┬──────┘
          │       │devolver       │ aprobar
          │       │               │
          │       ▼               ▼
          │ ┌──────────┐  ┌──────────────┐
          └►│EN_AJUSTE │  │PENDIENTE_APR │
            └────┬─────┘  └──────┬──────┘
                 │               │ aprobar
                 │               ▼
                 │         ┌──────────────┐
                 │         │   APROBADO   │
                 │         └──────┬───────┘
                 │                │
                 └────────────────┘
                          │
                          ▼
                 ┌──────────────┐
                 │DOCUMENTO_GEN │
                 └──────┬───────┘
                        │ generar
                        ▼
                 ┌──────────────┐
                 │   RADICADO   │─────► EN_SEGUIMIENTO ──► CERRADO
                 └──────────────┘
```

## Frontend Pages

```
/                           → Tablero general
/expedientes/new            → Crear expediente
/expedientes/{id}           → Vista del expediente (fases)
/expedientes/{id}/fases/{n} → Formulario de fase N
/expedientes/{id}/historial  → Historial y trazabilidad
```

## Tech Stack para este Change

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI + Python 3.11+ |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| DB | PostgreSQL 15+ |
| Frontend | Next.js 15 (App Router) |
| UI | Tailwind CSS + shadcn/ui |
| Auth | Basic JWT (Keycloak viene después) |
| File Storage | Local filesystem (MinIO viene después) |

## Implementation Order

1. Estructura del proyecto (FastAPI + Next.js)
2. Modelo de datos y migraciones
3. CRUD de expedientes y fases
4. Estados y transiciones
5. Carga de evidencias
6. Observaciones y devoluciones
7. Historial de versiones
8. Tablero de control
9. Auditoría básica