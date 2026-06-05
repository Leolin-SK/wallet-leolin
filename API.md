# 📡 Documentation API — Wallet Léolin

Base URL locale : `http://localhost:8000/api`
Base URL production : `https://ton-app.railway.app/api`
Documentation interactive : `http://localhost:8000/api/docs/`

---

## 🔐 AUTHENTIFICATION

Tous les endpoints (sauf login/register) requièrent un header :
```
Authorization: Bearer <access_token>
```

### POST /auth/register/
Créer un compte
```json
// Body
{ "username": "leolin", "email": "leolin@email.com",
  "first_name": "Léolin", "last_name": "Kameni",
  "password": "monmotdepasse", "password2": "monmotdepasse" }

// Réponse 201
{ "message": "Compte créé avec succès. Bienvenue Léolin ! 🎉", "username": "leolin" }
```

### POST /auth/login/
Connexion — retourne les tokens JWT
```json
// Body
{ "username": "leolin", "password": "monmotdepasse" }

// Réponse 200
{ "access": "eyJ...", "refresh": "eyJ..." }
```

### POST /auth/refresh/
Rafraîchir le token d'accès
```json
// Body
{ "refresh": "eyJ..." }
// Réponse 200
{ "access": "eyJ..." }
```

---

## 🏠 DASHBOARD

### GET /dashboard/
Toutes les données pour le tableau de bord
```json
// Réponse 200
{
  "solde_eur": 5842.50,
  "solde_fcfa": 3831245.0,
  "solde_initial_eur": 6107.0,
  "pourcentage_capital": 95.7,
  "total_revenus_eur": 1235.0,
  "total_depenses_eur": 1499.50,
  "mois_revenus_eur": 700.0,
  "mois_depenses_eur": 622.0,
  "mois_solde_eur": 78.0,
  "total_famille_eur": 100.0,
  "total_epargne_eur": 50.0,
  "health_level": "excellent",
  "alertes": [
    { "level": "good", "icon": "💰", "text": "Excédent de 78.0€ ce mois !" }
  ],
  "evolution_mensuelle": [
    { "mois": 11, "annee": 2026, "label": "Nov", "revenus": 700.0, "depenses": 622.0, "net": 78.0 }
  ]
}
```

---

## 💸 TRANSACTIONS

### GET /transactions/
Liste des transactions (avec filtres optionnels)
```
?mois=11&annee=2026&type=expense&category=1
```

### POST /transactions/
Créer une transaction
```json
// Body
{
  "category": 1,
  "type_tx": "expense",
  "label": "Lidl courses",
  "montant_eur": "35.50",
  "date": "2026-11-15",
  "note": "Semaine 2",
  "is_recurrent": false
}
// Réponse 201 : transaction créée avec montant_fcfa calculé automatiquement
```

### PUT /transactions/{id}/
Modifier une transaction

### DELETE /transactions/{id}/
Supprimer une transaction

### POST /transactions/repartir/
Répartition automatique d'un montant
```json
// Body
{ "montant_eur": 700 }

// Réponse 200
{
  "montant_total_eur": 700.0,
  "montant_total_fcfa": 459169,
  "repartition": [
    { "category_nom": "Loyer", "category_icone": "🏠",
      "pourcentage": 51.4, "montant_budget_eur": 320.0,
      "montant_alloue_eur": 359.8, "montant_alloue_fcfa": 235999 },
    ...
  ]
}
```

### GET /transactions/stats/
Statistiques par catégorie pour un mois donné
```
?mois=11&annee=2026
```

---

## 📋 CATÉGORIES

### GET /categories/
Liste toutes les catégories avec dépenses actuelles

### POST /categories/
Créer une catégorie
```json
{ "nom": "Loisirs", "icone": "🎉", "couleur": "#818cf8",
  "type_cat": "variable", "budget_mensuel": "30.00" }
```

---

## 🎯 OBJECTIFS

### GET /objectifs/
Liste des objectifs avec progression

### POST /objectifs/
Créer un objectif
```json
{ "label": "Vélo neuf", "icone": "🚲", "couleur": "#4ade80",
  "montant_cible_eur": "150.00", "date_limite": "2027-03-01" }
```

### POST /objectifs/{id}/alimenter/
Ajouter un montant à un objectif
```json
{ "montant_eur": 50 }
```

---

## 🔄 RÉCURRENTES

### GET /recurrentes/
Liste des dépenses récurrentes

### POST /recurrentes/{id}/appliquer/
Enregistrer cette récurrente comme transaction du jour
```json
// Réponse 200
{ "message": "Loyer mensuel enregistré avec succès.", "transaction": { ... } }
```

---

## 🌍 TRANSFERTS FAMILLE

### POST /transferts/simuler/
Simuler un transfert et comparer les prestataires
```json
// Body
{ "montant_eur": 100 }

// Réponse 200
{
  "montant_envoye_eur": 100,
  "taux_fcfa": 655.957,
  "resultats": [
    { "id": "orange", "name": "Orange Money", "frais_eur": 0,
      "montant_net_eur": 100, "montant_fcfa": 65596, "is_best": true },
    { "id": "sendwave", "name": "Sendwave", "frais_eur": 1.0,
      "montant_net_eur": 99, "montant_fcfa": 64940, "is_best": false },
    ...
  ]
}
```

---

## 📊 ANALYSE

### GET /analyse/
Analyse complète + plan de structuration
```
?mois=11&annee=2026
```
```json
// Réponse 200
{
  "mois": 11, "annee": 2026,
  "revenus_eur": 700.0, "depenses_eur": 622.0, "solde_mois_eur": 78.0,
  "recommandations": [
    { "level": "good", "icon": "🟢", "text": "Transport : excellent contrôle — 0€ d'économies ce mois." }
  ],
  "reste_a_allouer": [
    { "category": "Alimentation", "icone": "🍽️", "restant_eur": 65.0, "restant_fcfa": 42637 }
  ],
  "actions_prioritaires": [
    { "icon": "🏦", "text": "Transfère 23.4€ vers l'épargne Année 2 maintenant" },
    { "icon": "🍽️", "text": "Too Good To Go 3× cette semaine → économise ~10€" },
    { "icon": "📊", "text": "Reviens analyser chaque vendredi soir" }
  ]
}
```

---

## 👤 PROFIL

### GET /profile/
Lire son profil avec solde calculé

### PUT /profile/
Modifier son profil
```json
{ "solde_initial": 6107.00, "devise_preference": "FCFA",
  "seuil_alerte": 2000.00, "objectif_famille_annuel": 1000.00 }
```

---

## 🔧 CODES D'ERREUR

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 201 | Créé avec succès |
| 400 | Données invalides |
| 401 | Non authentifié / Token expiré |
| 403 | Accès refusé |
| 404 | Ressource introuvable |
| 500 | Erreur serveur |
