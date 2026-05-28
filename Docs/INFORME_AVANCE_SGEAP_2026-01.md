# INFORME DE AVANCE - SGEAP

## Sistema de Gestión de Expedientes Académicos para Programas

### Corporación Universitaria Adventista - UNAC

### Período: Enero - Mayo 2026

---

## 1. COMPROMISOS ADQUIRIDOS POR EL PROYECTO

### Del PRD (Documento de Alcance v2):

**MVP - Alcance Inicial:**
- Crear expediente académico para programa nuevo o renovación
- Gestionar las diez fases del proceso institucional
- Incluir RAG institucional desde el inicio
- Planear integraciones directas con sistemas académico, financiero y talento humano
- Permitir validación humana antes de aprobar contenido generado por IA
- Generar documento maestro preliminar y reportes internos

**10 Fases Institucionales:**
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

**Integraciones Planeadas:**
- Sistema académico (solo lectura)
- Sistema financiero (solo lectura)
- Talento humano / carga académica (solo lectura)
- Investigación
- Proyección social
- Biblioteca
- Infraestructura

---

## 2. AVANCE ACTUAL DE LA INVESTIGACIÓN

### Fases Completadas:

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Levantamiento detallado (PRD) | ✅ Completo |
| 2 | Diseño funcional y UX | 🔄 En progreso |
| 3 | Arquitectura e infraestructura | 🔄 En progreso |
| 4 | MVP de expediente y flujo | 🔄 En desarrollo |

### Ruta de Implementación:
```
✅ Fase 1: Levantamiento detallado
🔄 Fase 2: Diseño funcional y UX (parcialmente)
🔄 Fase 3: Arquitectura e infraestructura (parcialmente)
🔄 Fase 4: MVP de expediente y flujo (EN DESARROLLO)
⬜ Fase 5: RAG institucional
⬜ Fase 6: Integraciones prioritarias
⬜ Fase 7: IA asistida y validaciones
⬜ Fase 8: Piloto institucional
```

### Pendiente de Investigación:
- Inventario técnico-funcional de fuentes institucionales y documentos RAG
- Diseño de arquitectura técnica detallada
- Modelo de datos completo
- Backlog de desarrollo detallado
- Prototipo navegable avanzado

---

## 3. RESULTADOS ALCANZADOS DURANTE EL PERÍODO 2026-01

### Software Desarrollado (MVP - Core):

**Backend (FastAPI):**
- API REST completa con autenticación JWT
- 8+ tablas en PostgreSQL (expedientes, fases, campos, evidencias, observaciones, versiones, audit_logs, users)
- CRUD completo de expedientes
- 10 fases institucionales auto-creadas al crear expediente
- Upload de evidencias
- Sistema de observaciones
- Historial de auditoría
- Generación de documento maestro (preview y generación)
- Gestión de usuarios (CRUD)

**Frontend (Next.js 15):**
- Dashboard con auth guard
- Login con JWT
- Crear expediente
- Vista detalle expediente con 10 fases
- Edición de fase con evidencias y observaciones
- Documento maestro preview
- Gestión de usuarios (admin)

**APIs Implementadas:**
- `/api/auth/*` - Login, registro
- `/api/expedientes/*` - CRUD + tablero + audit
- `/api/fases/*` - CRUD + estado + enviar-revision + aprobar
- `/api/fases/{id}/evidencias` - Upload/download/list
- `/api/fases/{id}/observaciones` - CRUD
- `/api/expedientes/{id}/documento-preview`
- `/api/expedientes/{id}/generar-documento`
- `/api/users/*` - CRUD usuarios

**13 Commits realizados:**
1. feat: SGEAP MVP - Backend API + Frontend Dashboard
2. feat: improve new expediente form
3. feat: fase detail page
4. feat: add audit endpoints
5. feat: add login page
6. feat: auth guards
7. fix: bcrypt compatibility
8. feat: auth headers in API
9. feat: add documento maestro API
10. feat: add documento maestro preview (frontend)
11. fix: handle undefined name in Navbar
12. feat: add users management API
13. feat: add users admin page

---

## 4. PRODUCTOS GENERADOS Y PROYECTADOS

### Productos Generados:

| Producto | Descripción | Estado |
|----------|-------------|--------|
| PRD v2 | Documento de Alcance Funcional y Arquitectura Conceptual | ✅ |
| MVP Backend | API FastAPI con PostgreSQL | ✅ Funcional |
| MVP Frontend | Aplicación Next.js 15 | ✅ Funcional |
| Memory del proyecto | Documentación de decisiones técnicas | ✅ |
| OpenSpec artifacts | Proposal, design, specs, tasks para core-expediente-fases | ✅ |

### Productos Proyectados (pendientes):

| Producto | Prioridad | Dependencias |
|----------|----------|--------------|
| RAG institucional | Alta | MVP Base |
| Integración sistema académico | Alta | MVP Base + Capa de integración |
| Integración sistema financiero | Media | MVP Base |
| Módulo de IA asistida | Media | RAG institucional |
| Piloto institucional | Alta | MVP Completo |
| Despliegue Docker | Media | MVP + RAG |

---

## 5. CONCLUSIONES Y PRÓXIMOS PASOS

### Estado Actual:
El proyecto cuenta con un MVP funcional que demuestra la gestión de expedientes académicos por fases, pero aún faltan componentes críticos del alcance original.

### Próximos Pasos Inmediatos:
1. Completar debugging de interfaz de usuarios
2. Integrar RAG institucional
3. Planear integraciones con sistemas fuentes
4. Piloto con expediente real

---

*Documento generado: 2026-05-20*
*Ubicación del proyecto: E:\Projects\appsgeap*
*Documento base: Docs/PRD/Documento_Alcance_Sistema_Programas_Academicos_UNAC_v2_Tecnologias.docx*