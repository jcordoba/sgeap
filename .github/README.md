# GitHub Actions - Configuración

## Secrets Requeridos

### Frontend (Vercel)
```bash
gh secret set VERCEL_TOKEN --body "tu-vercel-token"
gh secret set VERCEL_ORG_ID --body "tu-org-id"
gh secret set VERCEL_PROJECT_ID --body "tu-project-id"
```

### Backend
```bash
gh secret set DATABASE_URL --body "postgresql://user:pass@host:5432/dbname"
```

## Habilitar Deploy

1. Editar `.github/workflows/deploy.yml`
2. Cambiar `if: false` a `if: true` en el step de deploy que uses
3. Configurar los secrets correspondientes

## Workflows Disponibles

- **CI**: Se ejecuta en cada PR y push a main
- **Deploy**: Se ejecuta en push a main (manual con workflow_dispatch)
