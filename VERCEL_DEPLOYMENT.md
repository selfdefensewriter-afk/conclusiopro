# Déploiement sur Vercel

## Étapes

### 1. Pusher le code vers GitHub
Utilisez le bouton "Save to Github" dans Emergent.

### 2. Connecter à Vercel
1. Allez sur [vercel.com](https://vercel.com)
2. Connectez-vous avec GitHub
3. Cliquez "Add New Project"
4. Importez votre repo `conclusiopro`

### 3. Configurer les variables d'environnement
Dans Vercel → Project Settings → Environment Variables, ajoutez:

| Variable | Valeur |
|----------|--------|
| `DATABASE_URL` | `postgresql://postgres.jmelzrjkustblcpnggps:Mauricia1944%2A@aws-1-eu-central-1.pooler.supabase.com:6543/postgres` |
| `GOOGLE_CLIENT_ID` | `1078798492889-uc5q8pibr00bvumjrj1mq3vr8lhp0lif.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | `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` |
| `SESSION_SECRET` | `votre_secret_aleatoire_ici` |
| `FRONTEND_URL` | `https://conclusiopro.vercel.app` (ou votre domaine Vercel) |
| `BACKEND_URL` | `https://conclusiopro.vercel.app` (même domaine) |

### 4. Mettre à jour Google OAuth
Dans Google Cloud Console → Credentials → OAuth Client:
- Ajoutez `https://votre-projet.vercel.app/api/auth/google/callback` aux Authorized redirect URIs

### 5. Déployer
Cliquez "Deploy" et attendez ~2 minutes.

## Structure du projet

```
/app
├── api/
│   ├── index.py         # Backend FastAPI (serverless)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── vercel.json          # Configuration Vercel
```

## Avantages de Vercel
- Déploiement instantané (~30 secondes)
- CDN global (ultra rapide)
- HTTPS automatique
- Gratuit pour les projets personnels
