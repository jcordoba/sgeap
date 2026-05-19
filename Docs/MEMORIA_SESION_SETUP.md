# Respaldo de Memoria - SGEAP
Generado: 2026-05-18
Actualizado: 2026-05-18

## Sesión de Setup e Inicio del Proyecto

### Contexto
Proyecto nuevo en E:\Projects\appsgeap basado en el documento PRD:
`Docs/PRD/Documento_Alcance_Sistema_Programas_Academicos_UNAC_v2_Tecnologias.docx`

Sistema: SGEAP (Sistema de Gestión de Expedientes Académicos para Programas)
Cliente: Corporación Universitaria Adventista - UNAC

### Stack Tecnologico
- Frontend: Next.js + React + TypeScript
- Backend: FastAPI + Python (NO NestJS como appvisitacion)
- DB: PostgreSQL + pgvector
- UI: Tailwind CSS + shadcn/ui
- Auth: Keycloak
- Storage: MinIO/S3
- Queues: Redis + Celery
- Deploy: Docker + Docker Swarm + Traefik

### Metodología
OpenSpec workflow copiado de appvisitacion
Comandos: /opsx:explore, /opsx:propose, /opsx:apply, /opsx:archive

### Decisiones Tomadas
1. MVP = esqueleto funcional (no piloto real)
2. Primer change: core-expediente-fases
3. Piloto viene después de MVP funcional (Fase 8)
4. RAG desde inicio del MVP
5. Integraciones en solo lectura

---

## Change: core-expediente-fases

### Estado
OpenSpec artifacts COMPLETOS (proposal, design, specs, tasks)
Preparado para /opsx:apply

### Ubicación
`openspec/changes/core-expediente-fases/`

### Estructura
```
core-expediente-fases/
├── .openspec.yaml
├── proposal.md           # What & Why
├── design.md             # Arquitectura, modelo datos, API
├── tasks.md              # 11 fases, ~50 tasks
└── specs/
    ├── expediente/       # CRUD expediente specs
    ├── fase/             # Workflow de fases specs
    ├── evidencia/        # Upload de evidencias specs
    ├── observacion/       # Observaciones specs
    └── tablero/           # Dashboard specs
```

### Modelo de Datos
- `expedientes` - cabecera del trámite
- `fases` - 10 fases por expediente (con estado individual)
- `campos` - valores clave-valor por fase
- `evidencias` - archivos subidos
- `observaciones` - comentarios/devoluciones
- `versiones` - historial de cambios
- `audit_logs` - trazabilidad completa

### API Endpoints
- Expedientes: POST, GET, GET/{id}, PUT, DELETE, /tablero
- Fases: GET, PUT, /estado, /enviar-revision, /aprobar
- Evidencias: POST upload, GET list, GET download, DELETE
- Observaciones: POST, GET
- Historial: GET /versiones, GET /audit

### Estados del Expediente
BORRADOR → EN_FORMULACION → EN_REVISION → CON_OBSERVACIONES → EN_AJUSTE → VALIDADO_TECNICAMENTE → PENDIENTE_APROBACION → APROBADO → DOCUMENTO_GENERADO → RADICADO → EN_SEGUIMIENTO → CERRADO

### Fases de Implementación (tasks.md)
1. Project Setup (FastAPI + Next.js)
2. Database Model (SQLAlchemy + migrations)
3. Expediente API (CRUD)
4. Fase API (workflow)
5. Evidence Upload (archivos)
6. Observations
7. Version History (auditoría)
8. Dashboard (tablero)
9. Expediente Views (UI)
10. History View (UI)
11. Polish (errors, loading, empty states)

### Tech Stack para MVP inicial
- Backend: FastAPI + SQLAlchemy 2.0 + Alembic
- Frontend: Next.js 15 + Tailwind + shadcn/ui
- Auth: JWT básico (Keycloak después)
- Storage: filesystem local (MinIO después)

---

## Paleta de Colores Institucionales - UNAC

**Fuente:** Pantallas de SION (PantallaDeInicio.png, Dashboard.png, PantallaModuloCalidad.png, Administrador.png)

```css
--color-primary:     #1E3F6F;  /* Azul navy — dominante */
--color-accent:      #F5A623;  /* Amarillo — solo CTA y acentos */
--color-text:        #2D2D2D;  /* Texto principal */
--color-text-muted:  #6B7280;  /* Texto secundario */
--color-link:        #295884;  /* Links e interactivos */
--color-bg:          #F5F7FA;  /* Fondo general */
--color-card:        #FFFFFF;  /* Cards y contenedores */
--color-border:      #D9DDE3;  /* Bordes */
--font-family:       'Montserrat', sans-serif;
```

### Reglas de uso
- `#1E3F6F` es el color institucional dominante (navbar, headers, botones primarios)
- `#F5A623` solo para botones CTA destacados y acentos puntuales
- No usar `#303520` en ningún lugar
- Diseño moderno y responsivo, no replicar la interfaz vieja de SION