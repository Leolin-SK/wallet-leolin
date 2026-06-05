# 🚀 Guide d'installation — Wallet Léolin Système Complet

## PRÉREQUIS
- Python 3.10+ → python.org
- Node.js 18+ → nodejs.org
- Git → git-scm.com

---

## ⚙️ BACKEND DJANGO

### 1. Se placer dans le dossier backend
```bash
cd wallet-system/backend
```

### 2. Créer l'environnement virtuel Python
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Créer le fichier .env (copie du .env.example)
```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```
Ouvre `.env` et modifie `SECRET_KEY` avec une vraie clé aléatoire.

### 5. Initialiser la base de données
```bash
python manage.py migrate
```

### 6. Créer un compte administrateur
```bash
python manage.py createsuperuser
# Saisis : username, email, password
```

### 7. Lancer le serveur Django
```bash
python manage.py runserver
```
✅ API disponible sur : http://localhost:8000/api/
✅ Admin Django : http://localhost:8000/admin/
✅ Docs API interactive : http://localhost:8000/api/docs/

---

## ⚛️ FRONTEND REACT

### 1. Ouvrir un nouveau terminal et aller dans frontend
```bash
cd wallet-system/frontend
```

### 2. Installer les dépendances Node
```bash
npm install
```

### 3. Lancer le frontend
```bash
npm start
```
✅ App disponible sur : http://localhost:3000

---

## 🌐 DÉPLOIEMENT EN LIGNE

### Backend → Railway (gratuit)

1. Va sur **railway.app** → crée un compte
2. "New Project" → "Deploy from GitHub repo"
3. Sélectionne ton repo → dossier `backend`
4. Dans les variables d'environnement Railway, ajoute :
   ```
   SECRET_KEY=une-cle-tres-longue-et-aleatoire
   DEBUG=False
   ALLOWED_HOSTS=ton-app.railway.app
   ```
5. Railway détecte automatiquement le `Procfile` et lance gunicorn
6. Note l'URL Railway : `https://ton-app.railway.app`

### Frontend → Vercel (gratuit)

1. Va sur **vercel.com** → crée un compte
2. "New Project" → importe ton repo GitHub
3. Configure :
   - Root Directory : `frontend`
   - Build Command : `npm run build`
   - Output Directory : `build`
4. Dans les variables d'environnement Vercel :
   ```
   REACT_APP_API_URL=https://ton-app.railway.app/api
   ```
5. Deploy → note ton URL Vercel

### Dernière étape : mettre à jour les CORS
Dans Railway, ajoute la variable :
```
CORS_ALLOWED_ORIGINS=https://ton-app.vercel.app
```

---

## 📱 ACCÈS DEPUIS L'iPHONE

Une fois déployé sur Vercel :
1. Ouvre Safari sur iPhone
2. Va sur `https://ton-app.vercel.app`
3. Partager → "Sur l'écran d'accueil"
4. Tu as une PWA qui ressemble à une vraie app !

---

## 🗂️ STRUCTURE FINALE DU PROJET

```
wallet-system/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      ← Configuration Django
│   │   ├── urls.py          ← Routes principales
│   │   └── wsgi.py
│   ├── wallet/
│   │   ├── models.py        ← Structure base de données
│   │   ├── serializers.py   ← Conversion données ↔ JSON
│   │   ├── views.py         ← Logique métier API
│   │   ├── urls.py          ← Routes de l'app
│   │   ├── admin.py         ← Interface admin
│   │   └── apps.py
│   ├── manage.py
│   ├── requirements.txt     ← Dépendances Python
│   ├── Procfile             ← Config déploiement Railway
│   └── .env.example         ← Variables d'environnement
├── frontend/
│   ├── src/
│   │   ├── App.js           ← Point d'entrée + routing
│   │   ├── index.js         ← Montage React
│   │   ├── context/
│   │   │   └── AuthContext.js  ← Gestion auth globale
│   │   ├── pages/
│   │   │   ├── LoginPage.js    ← Page connexion/inscription
│   │   │   └── Dashboard.js    ← App principale
│   │   └── services/
│   │       └── api.js          ← Tous les appels API
│   ├── package.json
│   ├── .env                 ← Variables React
│   └── vercel.json          ← Config déploiement Vercel
└── docs/
    ├── API.md               ← Documentation API complète
    └── INSTALL.md           ← Ce fichier
```

---

## 🔑 ENDPOINTS PRINCIPAUX

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | /api/auth/register/ | Créer un compte |
| POST | /api/auth/login/ | Se connecter |
| GET | /api/dashboard/ | Données tableau de bord |
| GET/POST | /api/transactions/ | Liste / Créer transaction |
| POST | /api/transactions/repartir/ | Répartition automatique |
| GET | /api/analyse/ | Analyse + recommandations |
| POST | /api/transferts/simuler/ | Simuler transfert famille |
| GET/POST | /api/objectifs/ | Objectifs financiers |
| GET/POST | /api/recurrentes/ | Dépenses récurrentes |

---

## ❓ DÉPANNAGE COURANT

**Erreur CORS** → Vérifie que `CORS_ALLOWED_ORIGINS` contient bien `http://localhost:3000`

**Token JWT expiré** → Le frontend le rafraîchit automatiquement. Sinon, reconnecte-toi.

**Module not found (Python)** → Vérifie que le venv est bien activé (`venv\Scripts\activate`)

**Port 8000 déjà utilisé** → `python manage.py runserver 8001` et change `REACT_APP_API_URL` dans `.env`
