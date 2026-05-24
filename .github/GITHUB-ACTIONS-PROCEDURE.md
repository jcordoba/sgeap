# GitHub Actions - Procedimiento de Configuración

Plantilla estándar para configurar CI/CD con GitHub Actions en cualquier proyecto.

---

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Workflow 1: CI (Integración Continua)](#workflow-1-ci-integración-continua)
4. [Workflow 2: Deploy](#workflow-2-deploy)
5. [Configuración de Secrets](#configuración-de-secrets)
6. [Configuración del Repositorio](#configuración-del-repositorio)
7. [Branch Protection Rules](#branch-protection-rules)
8. [Validación Local](#validación-local)
9. [Workflows Opcionales](#workflows-opcionales)
10. [Monitoreo y Debugging](#monitoreo-y-debugging)
11. [Cheat Sheet](#cheat-sheet)

---

## Requisitos Previos

### Software Necesario

| Herramienta | Versión Mínima | Propósito |
|-------------|----------------|-----------|
| Git | 2.30+ | Control de versiones |
| Node.js | 18+ | Runtime para CI |
| npm/pnpm/yarn | Latest | Package manager |
| GitHub CLI (opcional) | 2.0+ | Gestión de repos desde CLI |
| act (opcional) | Latest | Simular workflows localmente |

### Permisos Requeridos

- Owner o Admin del repositorio en GitHub
- Acceso a Settings del repositorio
- Capacidad de agregar Secrets y variables

### Verificaciones Iniciales

```bash
# 1. Verificar que el repositorio existe y es accesible
gh repo view

# 2. Verificar estado de git
git status

# 3. Verificar que el proyecto tiene scripts de build/test configurados
cat package.json | jq '.scripts'
```

---

## Estructura de Archivos

### Estructura Esperada

```
.github/
  workflows/
    ci.yml              # Integración continua
    deploy.yml         # Despliegue
    release.yml        # Versionado (opcional)
  actions/
    custom-action/     # Acciones personalizadas (opcional)
```

### Crear la Estructura Base

```bash
# Crear directorio .github si no existe
mkdir -p .github/workflows

# Verificar estructura
ls -la .github/
```

---

## Workflow 1: CI (Integración Continua)

### Propósito

Ejecutar en cada Pull Request y push a main para validar que:
- El código pasa linting
- Los tests pasan
- El build compila correctamente
- No hay errores de tipos (TypeScript)

### Flujo de Ejecución

```
PR/Push → Checkout → Setup Node → Install → Lint → Test → Build → Done
```

### Archivo: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  # Ejecutar en Pull Requests que apuntan a main
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize, reopened]

  # Ejecutar en pushes a estas ramas
  push:
    branches: [main, develop]

  # Permitir ejecución manual desde Actions tab
  workflow_dispatch:
    inputs:
      runner:
        description: 'Runner override (opcional)'
        required: false
        default: ''

jobs:
  # Job 1: Validación de código
  validate:
    name: Validate Code
    runs-on: ubuntu-latest

    # Timeout para evitar jobs colgados
    timeout-minutes: 15

    steps:
      # Step 1: Descargar código
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Necesario para algunos linters

      # Step 2: Configurar Node.js con cache
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'  # O 'pnpm' o 'yarn' según tu proyecto

      # Step 3: Instalar dependencias
      - name: Install dependencies
        run: npm ci
        # Si usas pnpm:
        # run: corepack enable && pnpm install --frozen-lockfile

      # Step 4: Linting
      - name: Run linter
        run: npm run lint
        continue-on-error: true  # Cambiar a false cuando el lint esté limpio

      # Step 5: Type check
      - name: Type check
        run: npm run typecheck
        # Equivalente: npx tsc --noEmit

      # Step 6: Tests unitarios
      - name: Run unit tests
        run: npm run test:unit
        # Si usas Vitest:
        # run: npm run test:unit -- --reporter=junit --outputFile=test-results.xml

      # Step 7: Tests de integración
      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

      # Step 8: Build de verificación
      - name: Verify build
        run: npm run build
        # Build en modo CI (sin watchers)
        # run: npm run build:ci

  # Job 2: Validación de cambios en base de datos (Prisma/Drizzle)
  db-migrate:
    name: Database Migrations
    runs-on: ubuntu-latest
    timeout-minutes: 10

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Validate Prisma schema
        run: cd apps/api && npx prisma validate

      - name: Check migration status
        run: cd apps/api && npx prisma migrate status
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test

  # Job 3: Tests E2E (requiere base de datos completa)
  e2e:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    timeout-minutes: 30

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Setup Prisma
        run: cd apps/api && npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test

      - name: Run E2E tests
        run: npm run test:e2e
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          CYPRESS_BASE_URL: http://localhost:3000

      # Guardar screenshots/videos de tests fallidos
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots
          path: apps/web/cypress/screenshots/
          retention-days: 7

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-videos
          path: apps/web/cypress/videos/
          retention-days: 7

  # Job 4: Análisis de seguridad
  security:
    name: Security Audit
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run npm audit
        run: npm audit --audit-level=high

      - name: Check for secrets in code
        uses: trufflesecurity/trufflehog@latest
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

### Configuración de Node.js Cache

```yaml
# Opción 1: npm
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

# Opción 2: pnpm
- uses: actions/setup-node@v4
  with:
    node-version: '20'

- name: Enable pnpm
  run: corepack enable && corepack prepare pnpm@latest --activate

- name: Get pnpm cache directory
  id: pnpm-cache
  shell: bash
  run: echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT

- name: Setup pnpm cache
  uses: actions/cache@v4
  with:
    path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
    key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
    restore-keys: |
      ${{ runner.os }}-pnpm-store-

# Opción 3: yarn
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'yarn'
```

---

## Workflow 2: Deploy

### Propósito

Desplegar la aplicación a producción cuando se hace merge a main.

### Flujo de Ejecución

```
Merge to Main → Checkout → Build → Package → Upload → Deploy → Verify
```

### Opciones de Deploy

#### Opción A: VPS (Virtual Private Server)

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment || 'production' }}
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment || 'production' }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Generate Prisma client
        run: cd apps/api && npx prisma generate

      - name: Build application
        run: npm run build

      - name: Create deployment package
        run: tar -czf deploy.tar.gz apps/ scripts/ package.json package-lock.json

      - name: Upload to VPS
        uses: appleboy/scp-action@v0.1.6
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          source: "deploy.tar.gz"
          target: "/home/opsmgr/stacks/PROJECT_NAME/"
          strip_components: 0

      - name: Deploy to VPS
        uses: appleboy/ssh-action@v0.1.6
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          envs: DB_URL,JWT_SECRET,FRONTEND_URL
          script: |
            set -e
            cd /home/opsmgr/stacks/PROJECT_NAME
            tar -xzf deploy.tar.gz
            rm -f deploy.tar.gz
            chmod +x scripts/deploy.sh
            bash scripts/deploy.sh "$DB_URL" "$JWT_SECRET" "$FRONTEND_URL"

      - name: Verify deployment
        run: curl -f https://tu-dominio.com/health || exit 1
```

#### Opción B: Vercel

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: apps/web
```

#### Opción C: Fly.io

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Flyctl
        uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        run: flyctl deploy --app ${{ secrets.FLY_APP }} --env production
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

#### Opción D: Docker + Container Registry

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
    tags:
      - 'v*'  # Solo en tags que empiezan con v

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest,enable={{ is_default_branch }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## Configuración de Secrets

### Cómo Agregar Secrets

#### Método 1: GitHub Web Interface

1. Ir a **Settings** del repositorio
2. En sidebar: **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Ingresar nombre y valor
5. Click **Add secret**

#### Método 2: GitHub CLI

```bash
# Agregar secret individual
gh secret set VPS_HOST --body "tu-servidor.com"

# Agregar secret desde archivo (para SSH keys)
gh secret set VPS_SSH_KEY < ~/.ssh/id_rsa

# Listar secrets
gh secret list

# Eliminar secret
gh secret delete VPS_HOST
```

### Secrets Comunes por Tipo de Proyecto

#### Proyecto Node.js/Express/Next.js

```bash
# Base de datos
gh secret set DATABASE_URL --body "postgresql://user:pass@host:5432/dbname"
gh secret set TEST_DATABASE_URL --body "postgresql://user:pass@localhost:5432/test"

# Autenticación
gh secret set JWT_SECRET --body "$(openssl rand -hex 64)"
gh secret set JWT_EXPIRES_IN --body "7d"

# URLs
gh secret set FRONTEND_URL --body "https://tu-dominio.com"
gh secret set API_URL --body "https://api.tu-dominio.com"

# OAuth (si aplica)
gh secret set GOOGLE_CLIENT_ID --body "xxx"
gh secret set GOOGLE_CLIENT_SECRET --body "xxx"
gh secret set GITHUB_CLIENT_ID --body "xxx"
gh secret set GITHUB_CLIENT_SECRET --body "xxx"

# Email
gh secret set SMTP_HOST --body "smtp.gmail.com"
gh secret set SMTP_USER --body "tu@email.com"
gh secret set SMTP_PASSWORD --body "app-password"
```

#### Proyecto VPS

```bash
# SSH
gh secret set VPS_HOST --body "tu-servidor.com"
gh secret set VPS_USER --body "opsmgr"
gh secret set VPS_SSH_KEY < ~/.ssh/id_ed25519

# O si usas password en lugar de SSH key:
gh secret set VPS_PASSWORD --body "tu-password"
```

#### Proyecto Docker/Container

```bash
# Container Registry
gh secret set DOCKER_USERNAME --body "tu-usuario"
gh secret set DOCKER_TOKEN --body "token-de-accesso"

# Fly.io
gh secret set FLY_API_TOKEN --body "tu-token"
```

#### Proyecto Vercel

```bash
gh secret set VERCEL_TOKEN --body "tu-token"
gh secret set VERCEL_ORG_ID --body "tu-org-id"
gh secret set VERCEL_PROJECT_ID --body "tu-project-id"
```

### Variables de Entorno (no secretas)

Si hay variables que pueden ser públicas pero no deberían cambiar:

1. Ir a **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository variable**
3. Ingresar nombre y valor

```bash
# Variables comunes (no secretas)
gh variable set NODE_VERSION --body "20"
gh variable set NPM_REGISTRY --body "https://registry.npmjs.org"
```

---

## Configuración del Repositorio

### Permisos de Actions

**Ubicación:** Settings → Actions → General

Configurar en **Workflow permissions**:

```yaml
# En el YAML del workflow:
permissions:
  contents: read      # Checkout necesita esto
  pull-requests: write  # Para escribir comentarios en PRs
  deployments: write
  statuses: write
```

### Obtener Secrets del Repo Actual (Referencia)

```bash
# Ver qué secrets están configurados (sin valores)
gh secret list

# Ver variables configuradas
gh variable list

# Ver settings de Actions
gh api repos/:owner/:repo/actions/permissions
```

---

## Branch Protection Rules

### Configurar via GitHub Web

1. Ir a **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Configurar según needs:

#### Para main:

```
Rule name: main
☑ Require pull request reviews before merging
   - Required number of approvals: 1 (o más)
☑ Require status checks to pass before merging
   - Buscar jobs: validate, db-migrate, security
☑ Require branches to be up to date before merging
☑ Do not allow bypassing the above settings
☑ Include administrators
```

### Configurar via CLI

```bash
# Obtener branch protection actual
gh api repos/:owner/:repo/branches/main/protection

# Aplicar protección (ejemplo básico)
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["CI/validate","CI/security"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_approving_review_count":1}'
```

---

## Validación Local

### Opción 1: Simular con act

`act` permite ejecutar workflows de GitHub Actions localmente usando Docker.

```bash
# Instalar act (Windows con chocolatey)
choco install act-cli

# Instalar act (con npm)
npm install -g @nektos/act

# Listar workflows disponibles
act -l

# Ejecutar workflow de CI
act -W .github/workflows/ci.yml

# Ejecutar en modo verbose (ver output completo)
act -W .github/workflows/ci.yml -v

# Ejecutar con secrets (crear archivo .actrc)
echo "--secret-file .secrets.env" > .actrc
# Crear .secrets.env con formato:
# DATABASE_URL=postgresql://...
```

### Opción 2: Scripts de Validación Pre-commit

Agregar en `package.json`:

```json
{
  "scripts": {
    "precommit": "npm run lint && npm run typecheck && npm run test:unit",
    "build:ci": "NODE_ENV=production npm run build",
    "test:ci": "npm run test -- --ci --runInBand"
  }
}
```

Y configurar un hook pre-commit (con Husky):

```bash
# Instalar Husky
npm install -D husky

# Inicializar
npx husky init

# Agregar hook
echo "npm run precommit" > .husky/pre-commit
```

### Opción 3: Docker Compose para Tests Locales

`docker-compose.yml` para levantar servicios de test:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Bajar servicios
docker-compose down

# Bajar y eliminar datos
docker-compose down -v
```

---

## Workflows Opcionales

### Workflow 3: Release con Versionado

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            ghcr.io/${{ github.repository }}:latest
```

### Workflow 4: Dependabot Automatizado

`.github/dependabot.yml` (ubicación especial, no en workflows/):

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
    reviewers:
      - "owner"
    groups:
      production-dependencies:
        dependency-type: "production"
      development-dependencies:
        dependency-type: "development"
```

### Workflow 5: Notificaciones a Slack

```yaml
name: Notify

on:
  workflow_run:
    workflows: ["CI", "Deploy to VPS"]
    types: [completed]

jobs:
  notify:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion != 'success' }}

    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1.25.0
        with:
          payload: |
            {
              "text": "Workflow ${{ github.event.workflow_run.name }} failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Workflow Failed*\nRepository: ${{ github.repository }}\nWorkflow: ${{ github.event.workflow_run.name }}\nRun: ${{ github.event.workflow_run.html_url }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

### Workflow 6: Lighthouse CI

```yaml
name: Lighthouse CI

on: pull_request

jobs:
  lighthouseci:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.14.x
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
          LHCI_BUILD_TIMEOUT: 300000
```

### Workflow 7: Snyk Security Scan

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

---

## Monitoreo y Debugging

### Ver Logs de un Workflow

```bash
# Listar runs recientes
gh run list --limit 10

# Ver detalle de un run específico
gh run view RUN_ID

# Ver logs de un step específico
gh run view RUN_ID --log

# Descargar artifacts
gh run download RUN_ID

# Re-ejecutar workflow fallido
gh run rerun RUN_ID

# Ver workflows activos
gh run list --status in_progress
```

### Debugging en Local

```bash
# Habilitar debug mode para act
DEBUG=* act -W .github/workflows/ci.yml

# Ver secrets usados
gh run view RUN_ID --log | grep -A2 "secret"
```

### Troubleshooting Común

| Problema | Solución |
|----------|----------|
| Job nunca termina | Agregar `timeout-minutes` al job |
| Cache no funciona | Verificar que `cache: 'npm'` es correcto para tu package manager |
| Permission denied (SSH) | Verificar que `VPS_SSH_KEY` tiene el formato correcto (openssh) |
| Docker build falla | Usar `docker/setup-buildx-action@v3` |
| Postgres connection failed | Verificar que el service está configurado correctamente |
| Action deprecated | Buscar versión más reciente en GitHub Marketplace |

---

## Cheat Sheet

### Comandos Rápidos

```bash
# Gestión de secrets
gh secret set NAME --body "value"
gh secret list
gh secret delete NAME

# Gestión de variables
gh variable set NAME --body "value"
gh variable list

# Gestión de runs
gh run list
gh run view ID
gh run rerun ID
gh run cancel ID
gh run download ID

# Gestión de workflows
gh workflow list
gh workflow view NAME
gh workflow run NAME
gh workflow enable NAME
gh workflow disable NAME

# Gestión de artifacts
gh run download ID --name ARTIFACT_NAME

# Deshabilitar/Habilitar workflow
gh workflow disable ci.yml
gh workflow enable ci.yml
```

### Templates Comunes por Framework

#### Next.js (standalone output)

```yaml
- name: Setup Next.js
  run: |
    npx nextTelemetry disable
    npx next build

- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: nextjs
    path: |
      .next/
      package.json
```

#### Turborepo

```yaml
- name: Build
  run: npx turbo build --filter=@app/api --filter=@app/web

- name: Deploy
  uses:Vercel/preview-deployment@v1
  with:
    token: ${{ secrets.VERCEL_TOKEN }}
    prod: true
```

#### NestJS

```yaml
- name: NestJS Build
  run: |
    npx @nestjs/cli build
    npx prisma migrate deploy
```

### Variables de Entorno Útiles

| Variable | Descripción |
|----------|-------------|
| `GITHUB_REF` | Rama o tag actual |
| `GITHUB_SHA` | Commit SHA |
| `GITHUB_RUN_ID` | ID del run actual |
| `GITHUB_RUN_NUMBER` | Número de run en este workflow |
| `GITHUB_REPOSITORY` | owner/repo |
| `GITHUB_TOKEN` | Token automático para auth |
| `GITHUB_ACTOR` | Usuario que trigger el workflow |
| `github.event.head_commit.message` | Mensaje del commit |
| `github.event.pull_request.title` | Título del PR |

### Permissions por Defecto

```yaml
permissions:
  contents: read        # Obligatorio
  pages: read           # Si usas GitHub Pages
  pull-requests: write   # Para comentarios en PR
  attestations: write   # Para SLSA provenance
  actions: read         # Para leer artifact metadata
  checks: write         # Para status checks
  security-events: write # Para code scanning
  id-token: write       # Para OIDC tokens
```

### Matrix Strategy

```yaml
jobs:
  test:
    strategy:
      matrix:
        node-version: [18, 20, 22]
        os: [ubuntu-latest, windows-latest]
      fail-fast: false  # No parar si uno falla
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
```

---

## Checklist Final

Después de configurar, verificar:

- [ ] `ci.yml` corre exitosamente en PR
- [ ] `deploy.yml` tiene permisos correctos
- [ ] Todos los secrets están configurados
- [ ] Branch protection rule está activa
- [ ] Al menos un status check requerido
- [ ] `workflow_dispatch` funciona (probar manualmente)
- [ ] Notificaciones llegan (Slack si está configurado)
- [ ] Logs son legibles y útiles

---

## Recursos Adicionales

- [Documentación oficial GitHub Actions](https://docs.github.com/en/actions)
- [Marketplace de Actions](https://github.com/marketplace?type=actions)
- [workflow syntax reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Encrypted secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)