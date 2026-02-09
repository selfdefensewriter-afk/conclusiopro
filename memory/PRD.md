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
- **Backend:** FastAPI (Python), Motor (MongoDB async)
- **Database:** MongoDB
- **Auth:** Google OAuth 2.0 (via Emergent Auth)
- **Payments:** Stripe Checkout
- **AI:** Google Gemini (Emergent LLM Key)

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
  - **Prévisualisation** des images et PDF directement dans l'interface (ajouté le 09/02/2025)

### Bug Fixes
- [x] **09/02/2025:** Corrigé erreur `findDOMNode is not a function` - remplacement de react-quill par Tiptap
- [x] **09/02/2025:** Corrigé route FastAPI pour `/pieces/reorder` (ordre des routes)

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

### P1 - Next Tasks
- [ ] Réintroduire les offres "Avancée" et "Sérénité" sur la page Pricing (après implémentation des fonctionnalités)

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
│   ├── server.py          # FastAPI app avec toutes les routes
│   ├── uploads/pieces/    # Stockage des fichiers uploadés
│   └── requirements.txt
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
└── docs/
    ├── FAQ.md
    ├── CGU.md
    └── offre.md
```

## Key DB Schemas

### users
```json
{
  "user_id": "string",
  "email": "string",
  "name": "string",
  "picture": "string",
  "credits": "int",
  "created_at": "datetime"
}
```

### pieces
```json
{
  "piece_id": "string",
  "conclusion_id": "string",
  "user_id": "string",
  "numero": "int",
  "nom": "string",
  "description": "string",
  "filename": "string",
  "original_filename": "string",
  "file_size": "int",
  "mime_type": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Legal Compliance
- Disclaimer omniprésent: "Cette application ne fournit aucun conseil juridique et ne remplace pas un avocat"
- L'IA fournit des suggestions pédagogiques, pas des conseils juridiques personnalisés
- Pages FAQ et CGU avec contenu validé juridiquement
