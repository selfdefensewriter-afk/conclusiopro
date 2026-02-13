# ConclusioPro - Product Requirements Document

## Original Problem Statement
Application web "Self-Defense Writer" pour aider les particuliers à rédiger leurs conclusions juridiques (pro se litigants).

**Pivot Légal Important:** L'application est un **outil pédagogique et assistant de rédaction**, PAS un service de conseil juridique. Elle aide l'utilisateur à structurer ses écrits, sans rédiger à sa place ni fournir de conseils juridiques personnalisés.

## Core Requirements
- Google Gemini pour l'assistance IA (génération de texte pédagogique)
- Google Authentication pour la gestion des utilisateurs
- Stripe pour le paiement (modèle de crédits)
- Modèle B2C avec offre "Essential" à 29€

## Tech Stack
- **Frontend:** React 19, Tiptap (éditeur riche), TailwindCSS, Shadcn/UI
- **Backend:** FastAPI (Python), SQLAlchemy
- **Database:** PostgreSQL (migré de MongoDB le 13/02/2026)
- **Auth:** Google OAuth 2.0 (custom avec Authlib)
- **Payments:** Stripe Checkout
- **AI:** Google Gemini (Emergent LLM Key)
- **Deployment:** Render.com (backend + frontend + PostgreSQL)

## What's Been Implemented

### Core Features (Completed)
- [x] Page d'accueil avec disclaimer légal
- [x] Authentification Google OAuth
- [x] Dashboard utilisateur avec affichage des crédits
- [x] Wizard multi-étapes pour créer une conclusion
- [x] **Éditeur de texte riche Tiptap** (remplace react-quill - corrigé le 09/02/2025)
- [x] Système de templates pré-définis (JAF, Pénal)
- [x] Intégration Stripe Checkout (webhook configuré)
- [x] Pages légales: FAQ, CGU, Tarifs
- [x] **Gestion des pièces jointes** (ajouté le 09/02/2025)
  - Upload de fichiers (PDF, images, Word, etc. - max 10 Mo)
  - Numérotation automatique (Pièce n°1, Pièce n°2, etc.)
  - Renommage et description des pièces
  - Réorganisation par drag & drop
  - Insertion de références dans le texte (ex: "voir Pièce n°3")
  - Bordereau de pièces généré automatiquement
  - **Prévisualisation** des images et PDF directement dans l'interface

### Bug Fixes & Migrations
- [x] **09/02/2025:** Corrigé erreur `findDOMNode is not a function` - remplacement de react-quill par Tiptap
- [x] **09/02/2025:** Corrigé route FastAPI pour `/pieces/reorder` (ordre des routes)
- [x] **13/02/2026:** **MIGRATION POSTGRESQL** - Résolu le problème de connexion SSL MongoDB Atlas sur Render
  - Migré la base de données de MongoDB/Motor vers PostgreSQL/SQLAlchemy
  - Toutes les tables créées: users, user_sessions, legal_conclusions, pieces, payment_transactions, code_civil_articles, conclusion_templates
  - L'authentification Google OAuth fonctionne maintenant correctement

## API Endpoints - Pièces

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/conclusions/{id}/pieces` | Upload d'une pièce (multipart/form-data) |
| GET | `/api/conclusions/{id}/pieces` | Liste des pièces d'une conclusion |
| PUT | `/api/conclusions/{id}/pieces/reorder` | Réorganiser les pièces |
| PUT | `/api/conclusions/{id}/pieces/{pieceId}` | Modifier nom/description |
| DELETE | `/api/conclusions/{id}/pieces/{pieceId}` | Supprimer une pièce |
| GET | `/api/pieces/{pieceId}/download` | Télécharger une pièce |

## Current Pricing
- **Offre Essentielle:** 29€ - 1 crédit pour générer une conclusion

## Prioritized Backlog

### P0 - RESOLVED
- [x] **CRITIQUE:** Authentification cassée sur Render - **RÉSOLU via migration PostgreSQL**

### P1 - Next Tasks
- [ ] Déployer les changements sur Render.com
  - Push le code vers GitHub
  - Mettre à jour les variables d'environnement sur Render:
    - `DATABASE_URL` = URL interne PostgreSQL
    - `GOOGLE_CLIENT_ID` et `GOOGLE_CLIENT_SECRET`
    - `FRONTEND_URL` et `BACKEND_URL`
- [ ] Réintroduire les offres "Avancée" et "Sérénité" sur la page Pricing

### P2 - Future Features
- [ ] **Offre Avancée:** Aide à la clarté, ton neutre, style judiciaire, vérifications formelles
- [ ] **Offre Sérénité:** Checklist procédurale, aide contextuelle

### P3 - Long Term
- [ ] Service de relecture par juriste certifié (human-in-the-loop)
- [ ] Système de parrainage vers avocats partenaires
- [ ] Export Word (.docx) en plus du PDF

## Architecture

```
/app
├── backend/
│   ├── server.py          # FastAPI app avec SQLAlchemy (PostgreSQL)
│   ├── uploads/pieces/    # Stockage des fichiers uploadés
│   ├── requirements.txt   # Inclut psycopg2-binary, sqlalchemy, asyncpg
│   └── .env               # DATABASE_URL, GOOGLE_*, etc.
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ConclusionEditor.js  # Tiptap editor + PiecesManager
│   │   │   ├── Dashboard.js
│   │   │   ├── PricingPage.js
│   │   │   └── ...
│   │   ├── components/
│   │   │   ├── PiecesManager.js     # Gestion des pièces jointes
│   │   │   └── ui/                  # Shadcn components
│   │   ├── styles/tiptap.css
│   │   └── ...
│   └── package.json
├── render.yaml            # Configuration Render.com (PostgreSQL)
└── docs/
    ├── FAQ.md
    ├── CGU.md
    └── offre.md
```

## Key DB Schemas (PostgreSQL)

### users
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  picture TEXT,
  credits INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE
);
```

### user_sessions
```sql
CREATE TABLE user_sessions (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  session_token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE
);
```

### legal_conclusions
```sql
CREATE TABLE legal_conclusions (
  id SERIAL PRIMARY KEY,
  conclusion_id VARCHAR(50) UNIQUE NOT NULL,
  user_id VARCHAR(50) NOT NULL,
  type VARCHAR(50) NOT NULL,
  parties JSON,
  faits TEXT,
  demandes TEXT,
  conclusion_text TEXT,
  status VARCHAR(50) DEFAULT 'draft',
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);
```

### pieces
```sql
CREATE TABLE pieces (
  id SERIAL PRIMARY KEY,
  piece_id VARCHAR(50) UNIQUE NOT NULL,
  conclusion_id VARCHAR(50) NOT NULL,
  user_id VARCHAR(50) NOT NULL,
  numero INTEGER NOT NULL,
  nom VARCHAR(255) NOT NULL,
  description TEXT,
  filename VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  file_size INTEGER NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);
```

## Legal Compliance
- Disclaimer omniprésent: "Cette application ne fournit aucun conseil juridique et ne remplace pas un avocat"
- L'IA fournit des suggestions pédagogiques, pas des conseils juridiques personnalisés
- Pages FAQ et CGU avec contenu validé juridiquement

## Deployment Instructions (Render.com)

### Variables d'environnement Backend
```
DATABASE_URL=postgresql://conclusiopro:xxx@dpg-xxx-a/conclusiopro (URL interne)
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_client_secret
FRONTEND_URL=https://conclusiopro-frontend.onrender.com
BACKEND_URL=https://conclusiopro-backend.onrender.com
SESSION_SECRET=généré_automatiquement
EMERGENT_LLM_KEY=votre_clé (optionnel, pour génération IA)
STRIPE_API_KEY=votre_clé (optionnel, pour paiements)
```

### Variables d'environnement Frontend
```
REACT_APP_BACKEND_URL=https://conclusiopro-backend.onrender.com
```
