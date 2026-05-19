# Proposal: core-expediente-fases

## What

Construir el núcleo del sistema SGEAP: gestión de expedientes académicos digitales con las 10 fases institucionales, estados, evidencias y trazabilidad.

## Why

El PRD define que el sistema debe gestionar expedientes académicos digitales (no solo documentos). El MVP requiere demostrar que el sistema puede crear y gestionar expedientes, trabajar por fases, exigir evidencias, validar coherencia y generar documento maestro.

Sin este módulo core, no hay nada que sostener: RAG, IA e integraciones necesitan el expediente como contexto.

## Scope

### Included
- Crear expediente (tipo: nuevo / renovación)
- Registrar datos generales: nombre, facultad, nivel, modalidad, lugar, responsable, tipo de trámite
- Gestionar 10 fases institucionales con estados
- Cargar y asociar evidencias a fases
- Control de estados por fase y por expediente
- Envío a revisión y recepción de observaciones
- Devolver, ajustar y validar fases
- Historial de cambios, versiones, observaciones y aprobaciones
- Tablero de control (avance, riesgos, pendientes, alertas)

### Not included (futuros changes)
- RAG institucional
- Integraciones con sistemas fuente
- IA asistida
- Generación de documento maestro
- Módulo de administración de usuarios/roles

## Design Decisions

### Modelo de datos
- `Expediente`: cabecera del trámite (tipo, programa, estado general)
- `Fase`: cada fase con estado individual y relación al expediente
- `Campo`: información estructurada por fase
- `Evidencia`: archivos asociados a fase o campo
- `Observacion`: comentarios de revisión/devolución
- `Version`: historial de cambios
- `AuditLog`: trazabilidad de acciones

### Estados del expediente
```
Borrador inicial → En formulación → En revisión interna → Con observaciones → En ajuste → Validado técnicamente → Pendiente de aprobación institucional → Aprobado institucionalmente → Documento maestro generado → Radicado → En seguimiento → Cerrado / finalizado
```

### Estados por fase
Igual que estados del expediente, pero por fase individual. Una fase puede avanzar independientemente.

### Permisos por rol
- LÍDER_DE_PROPUESTA: crear expediente, editar fases, cargar evidencias
- EQUIPO_ACADÉMICO: editar camposassigned
- DISEÑO_CURRICULAR: revisar fase 4
- DIRECCIÓN_DE_CALIDAD: revisar fases 5, 6, 7
- VICERRECTORÍA_ACADÉMICA: supervisar, aprobar fases 8+
- ADMIN: gestión completa

## Risks & Unknowns

1. **Desconocimiento del flujo real**: sección 17 del PRD indica que primero debe hacerse un levantamiento detallado del flujo real de aprobaciones. Este change asume un flujo estándar basado en el documento.

2. **Estructura de formularios**: aún no está definido el detalle de campos por fase. Los specs detallados vendrán en `specs/`.

3. **Storage de evidencias**: MinIO/S3 recomendado pero no confirmado. Empezamos con filesystem local.

4. **Autenticación**: Keycloak planificado pero no instalado. Primer MVP puede usar auth básico.

## Next

Crear `design.md` con arquitectura, modelo de datos y flujo de estados.