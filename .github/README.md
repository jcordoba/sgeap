# GitHub Actions - Configuración

## Secrets Requeridos

```bash
gh secret set VPS_HOST --body "154.12.234.98"
gh secret set VPS_USER --body "opsmgr"
gh secret set VPS_SSH_KEY --body "$(cat ~/.ssh/id_ed25519_opsmgr)"
gh secret set VPS_PORT --body "22"
gh secret set POSTGRES_PASSWORD --body "tu-password-para-postgres"
gh secret set MINIMAX_API_KEY --body "tu-api-key-minimax"
```

## En tu VPS

- Carpeta: `/home/opsmgr/stacks/appsgeap`
- Docker Swarm con Traefik (como asava-acueducto)
- Redes: `frontend` y `backend` (creadas automáticamente)

## Setup Inicial en VPS

```bash
# Conectar y clonar repo
cd /home/opsmgr/stacks/appsgeap
git clone https://github.com/tu-user/sgeap.git .

# Crear redes Docker si no existen
docker network create frontend 2>/dev/null || true
docker network create backend 2>/dev/null || true

# Crear archivo .env
cat > .env << 'EOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu-password-seguro
MINIMAX_API_KEY=tu-api-key
EOF
```

## Workflows

- **CI**: se ejecuta en cada PR y push a main
- **Deploy**: push a main o manual con workflow_dispatch

## Primer Deploy

1. Hacer push de los cambios al repo
2. Ir a Actions → Deploy workflow → Run workflow
3. Monitorear en VPS: `docker stack ps sgeap`
