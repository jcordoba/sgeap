# GitHub Actions - Configuración

## Secrets Requeridos

### VPS Deployment (sgeap.singularity.cyou)
```bash
gh secret set VPS_HOST --body "tu-vps-ip-o-dominio"
gh secret set VPS_USER --body "usuario-ssh"
gh secret set VPS_SSH_KEY --body "clave-privada-ssh"
gh secret set VPS_PORT --body "22"
gh secret set DATABASE_URL --body "postgresql://user:pass@host:5432/dbname"
```

### Ejemplo con IP:
```bash
gh secret set VPS_HOST --body "192.168.1.100"
gh secret set VPS_USER --body "root"
```

## Habilitar Deploy

1. Editar `.github/workflows/deploy.yml`
2. Descomentar/ajustar los steps de deploy según tu configuración de VPS
3. Configurar los secrets correspondientes en GitHub

## Workflows Disponibles

- **CI**: Se ejecuta en cada PR y push a main
- **Deploy**: Se ejecuta en push a main (manual con workflow_dispatch)
