# Guide de Déploiement Render.com - ConclusioPro

## Prérequis
- Compte GitHub avec le code source
- Compte Render (gratuit) : https://render.com
- Compte MongoDB Atlas (gratuit) : https://www.mongodb.com/atlas

---

## Étape 1 : Créer la base de données MongoDB Atlas (Gratuit)

1. Allez sur https://www.mongodb.com/atlas
2. Créez un compte gratuit
3. Créez un cluster **"M0 Free"**
4. Dans **Database Access** : créez un utilisateur avec mot de passe
5. Dans **Network Access** : ajoutez `0.0.0.0/0` (permet toutes les IPs)
6. Dans **Database** → **Connect** → **Connect your application**
7. Copiez l'URL de connexion :
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

---

## Étape 2 : Sauvegarder sur GitHub

1. Dans Emergent, cliquez sur **"Save to GitHub"**
2. Notez l'URL de votre repository

---

## Étape 3 : Déployer le Backend sur Render

1. Allez sur https://render.com et connectez-vous avec GitHub
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre repository GitHub
4. Configurez :
   - **Name** : `conclusiopro-backend`
   - **Region** : Frankfurt (EU Central)
   - **Branch** : `main`
   - **Root Directory** : `backend`
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Instance Type** : **Free**

5. Ajoutez les **Variables d'environnement** (Section "Environment") :
   ```
   MONGO_URL=mongodb+srv://<votre_url_mongodb_atlas>
   DB_NAME=conclusiopro
   CORS_ORIGINS=*
   EMERGENT_LLM_KEY=sk-emergent-7Ed7bCc19F89025595
   STRIPE_API_KEY=<votre_clé_stripe>
   ```

6. Cliquez sur **"Create Web Service"**
7. Attendez le déploiement (~5 min)
8. **Notez l'URL** générée (ex: `https://conclusiopro-backend.onrender.com`)

---

## Étape 4 : Déployer le Frontend sur Render

1. Cliquez sur **"New +"** → **"Static Site"** (gratuit, pas de cold start!)
2. Connectez le même repository
3. Configurez :
   - **Name** : `conclusiopro-frontend`
   - **Branch** : `main`
   - **Root Directory** : `frontend`
   - **Build Command** : `yarn install && yarn build`
   - **Publish Directory** : `build`

4. Ajoutez les **Variables d'environnement** :
   ```
   REACT_APP_BACKEND_URL=https://conclusiopro-backend.onrender.com
   ```
   (Remplacez par l'URL de votre backend de l'étape 3)

5. Cliquez sur **"Create Static Site"**

---

## Étape 5 : Ajouter BACKEND_URL au Backend

1. Retournez dans votre service backend sur Render
2. Allez dans **Environment** 
3. Ajoutez :
   ```
   BACKEND_URL=https://conclusiopro-backend.onrender.com
   ```

---

## Étape 6 : Configurer Stripe Webhook

1. Dashboard Stripe : https://dashboard.stripe.com/webhooks
2. **"Add endpoint"** :
   - **URL** : `https://conclusiopro-backend.onrender.com/api/webhook/stripe`
   - **Événements** : `checkout.session.completed`
3. Sauvegardez

---

## Étape 7 : Éviter le Cold Start avec UptimeRobot (IMPORTANT)

Le backend Render gratuit "dort" après 15 min. Solution :

1. Allez sur https://uptimerobot.com (gratuit)
2. Créez un compte
3. **"Add New Monitor"** :
   - **Monitor Type** : HTTP(s)
   - **Friendly Name** : ConclusioPro Backend
   - **URL** : `https://conclusiopro-backend.onrender.com/api/health`
   - **Monitoring Interval** : 5 minutes
4. Sauvegardez

→ UptimeRobot "pingera" votre backend toutes les 5 min = **plus de cold start !**

---

## Vérification finale

1. Ouvrez votre URL frontend
2. Testez la connexion Google
3. Créez une conclusion
4. Testez l'upload de pièces
5. Testez le paiement (mode test Stripe)

---

## URLs finales

- **Frontend** : `https://conclusiopro-frontend.onrender.com`
- **Backend** : `https://conclusiopro-backend.onrender.com`
- **Health Check** : `https://conclusiopro-backend.onrender.com/api/health`

---

## Coûts

| Service | Coût |
|---------|------|
| Render Frontend (Static Site) | Gratuit |
| Render Backend (Web Service) | Gratuit |
| MongoDB Atlas (M0) | Gratuit |
| UptimeRobot | Gratuit |
| **TOTAL** | **0 €/mois** |

---

## Support

- Logs Render : Dashboard → Service → Logs
- Documentation : https://render.com/docs
