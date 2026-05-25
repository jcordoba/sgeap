# GitHub Actions - Configuración

## Secrets Requeridos

```bash
gh secret set VPS_HOST --body "sgeap.singularity.cyou"
gh secret set VPS_USER --body "opsmgr"
gh secret set VPS_SSH_KEY --body "contenido-de-clave-privada-ssh"
gh secret set VPS_PORT --body "22"
gh secret set DATABASE_URL --body "postgresql://..."
```

## En tu VPS

- Carpeta: `/home/opsmgr/stacks/appsgeap`
- Nginx sirviendo frontend en `sgeap.singularity.cyou`
- Backend: uvicorn en puerto 8000

## Para generar SSH key en VPS:

```bash
# En el VPS
ssh-keygen -t ed25519 -f ~/.ssh/github_deploy -N ""
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys
```

Pegar contenido de `~/.ssh/github_deploy` (la privada) en el secret `VPS_SSH_KEY` de GitHub.

## Workflows

- **CI**: se ejecuta en cada PR y push a main
- **Deploy**: push a main o manual con workflow_dispatch
