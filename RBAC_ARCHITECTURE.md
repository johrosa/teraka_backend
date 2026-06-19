## 🏗️ Architecture RBAC Autonome

### Vue d'ensemble du système

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADMIN DJANGO (/admin/)                       │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │        HUB CENTRAL RBAC (/admin/rbac/)                    │   │
│  │                                                            │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                │   │
│  │  │  Importer RBAC  │  │  Statut RBAC    │                │   │
│  │  │ /rbac/import/   │  │ /rbac/status/   │                │   │
│  │  └────────┬────────┘  └────────┬────────┘                │   │
│  │           │                    │                         │   │
│  │  ┌────────▼────────┐  ┌────────▼────────┐                │   │
│  │  │   Base de       │  │   Dashboard     │                │   │
│  │  │   données       │  │   statistique   │                │   │
│  │  │   PostgreSQL    │  │                 │                │   │
│  │  └─────────────────┘  └─────────────────┘                │   │
│  │                                                            │   │
│  │  ┌──────────────────────────────────┐                     │   │
│  │  │  Gestion des rôles utilisateurs  │                     │   │
│  │  │    /core/userrole/               │                     │   │
│  │  └──────────────────────────────────┘                     │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Flux d'authentification & autorisation

```
┌──────────────┐
│  Utilisateur │
└──────┬───────┘
       │
       │ POST /api/login/ (username/password)
       ▼
┌──────────────────────────────────────┐
│    Django Auth Backend               │
│  - Vérifier les credentials          │
│  - Chercher le rôle de l'utilisateur │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  JWT Token générée                   │
│  Include: user_id, role, level       │
│  Exemple: {"role": "MRV_L2", "level": 2}│
└──────────────┬───────────────────────┘
               │
               │ Token retourné au client
               ▼
┌──────────────────────────────────────┐
│  Client stocke le token              │
│  (localStorage, sessionStorage, etc) │
└──────────────┬───────────────────────┘
               │
               │ GET /api/data/sites?...
               │ Header: Authorization: Bearer <token>
               ▼
┌──────────────────────────────────────┐
│    PostgREST Proxy                   │
│  - Valider le token JWT              │
│  - Extraire le rôle                  │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│    PostgreSQL Connection             │
│  SET ROLE 'MRV_L2';                 │
│  SELECT * FROM sites WHERE ...      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Row-Level Security (RLS)            │
│  - Vérifie permissions du rôle       │
│  - Retourne seulement les données    │
│    autorisées pour ce rôle           │
└──────────────┬───────────────────────┘
               │
               ▼
        ┌──────────────┐
        │  Données     │
        │  Retournées  │
        └──────────────┘
```

### Architecture des fichiers

```
backend_django/
├── config/
│   ├── urls.py ........................... MODIFIÉ (Routes RBAC)
│   ├── settings.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── views.py .......................... MODIFIÉ (rbac_hub_view)
│   ├── admin.py .......................... (RBACImportView, RBACStatusView)
│   ├── models.py
│   ├── serializers.py
│   ├── templates/
│   │   └── admin/
│   │       ├── rbac_hub.html ............ CRÉÉ (Template hub)
│   │       └── csv_form.html
│   └── migrations/
│
├── RBAC_README.md ..................... CRÉÉ (Vue rapide)
├── RBAC_GUIDE.md ...................... CRÉÉ (Documentation)
├── RBAC_AUTONOME_SUMMARY.md ........... CRÉÉ (Résumé technique)
├── DEPLOYMENT_CHECKLIST.md ........... CRÉÉ (Checklist déploiement)
├── test_rbac_urls.py ................. CRÉÉ (Tests)
│
└── manage.py
```

### URL Routing

```
/admin/
├── /rbac/ ........................... rbac_hub_view (GET)
│   └── Affiche: hub.html
│
├── /rbac/import/ ................... RBACImportView (GET/POST)
│   └── Formulaire d'import CSV/Excel
│
├── /rbac/status/ ................... RBACStatusView (GET)
│   └── Affiche les permissions RBAC
│
└── /core/userrole/ ................ Admin standard Django
    └── CRUD sur les rôles utilisateurs
```

### Intégration avec PostgREST

```
┌──────────────┐
│   Frontend   │
│   (React)    │
└──────┬───────┘
       │
       │ 1. POST /api/login/
       ▼
┌──────────────────────────────┐
│  Django Backend              │
│  - Auth check                │
│  - JWT + role généré         │
└──────┬───────────────────────┘
       │
       │ 2. Token JWT avec "role"
       ▼
┌──────────────────────────────┐
│  Frontend reçoit token       │
│  Stock localement            │
└──────┬───────────────────────┘
       │
       │ 3. GET /api/data/sites
       │    + Authorization: Bearer <JWT>
       ▼
┌──────────────────────────────┐
│  Reverse Proxy Django        │
│  - Valide JWT                │
│  - Route vers PostgREST      │
└──────┬───────────────────────┘
       │
       │ 4. Requête authentifiée
       │    SET ROLE 'MRV_L2'
       ▼
┌──────────────────────────────┐
│  PostgREST (Port 3000)       │
│  - Exécute avec le rôle      │
│  - RLS appliquée             │
└──────┬───────────────────────┘
       │
       │ 5. SELECT * FROM sites...
       ▼
┌──────────────────────────────┐
│  PostgreSQL                  │
│  - RLS policy check          │
│  - Permissions vérifiées     │
└──────┬───────────────────────┘
       │
       │ 6. Données filtrées
       ▼
        Résultat envoyé au frontend
```

### Cycle de vie de la gestion RBAC

```
1. ADMINISTRATEUR ACCÈDE À /admin/rbac/
   ↓
   ┌───────────────────────────────────┐
   │    HUB RBAC Affiché               │
   │  - 4 cartes principales           │
   │  - Informations sur les rôles     │
   └───────────────────────────────────┘
   ↓
2. ADMINISTRATEUR CHOISIT UNE ACTION
   ├─→ Importer la matrice
   │   ↓
   │   ┌─────────────────────────────┐
   │   │ Upload CSV/Excel            │
   │   │ /admin/rbac/import/         │
   │   └────────┬────────────────────┘
   │            ↓
   │   ┌─────────────────────────────┐
   │   │ Traitement:                 │
   │   │ - Créer rôles PostgreSQL    │
   │   │ - Appliquer permissions     │
   │   │ - Log des changements       │
   │   └────────┬────────────────────┘
   │            ↓
   │   Retour au hub
   │
   ├─→ Consulter le statut
   │   ↓
   │   ┌─────────────────────────────┐
   │   │ /admin/rbac/status/         │
   │   │ - Rôles configurés          │
   │   │ - Permissions par table     │
   │   │ - Utilisateurs assignés     │
   │   └────────┬────────────────────┘
   │            ↓
   │   Retour au hub
   │
   └─→ Gérer les rôles utilisateurs
       ↓
       ┌─────────────────────────────┐
       │ /admin/core/userrole/       │
       │ - Ajouter assignation       │
       │ - Modifier rôle             │
       │ - Voir historique           │
       └────────┬────────────────────┘
                ↓
       Retour au hub
```

### Sécurité - Niveaux de protection

```
1. AUTHENTIFICATION (Django Auth)
   ✓ Username/Password (POST /api/login/)
   ✓ JWT Token généré
   ✓ Expiration du token

2. AUTORISATION (Staff Required)
   ✓ @staff_member_required décorateur
   ✓ Accès admin seulement
   ✓ Vérification des permissions

3. PROTECTION CSRF
   ✓ Tokens CSRF sur formulaires
   ✓ Middleware Django automatique
   ✓ Validation serveur

4. ROW-LEVEL SECURITY (PostgreSQL)
   ✓ SET ROLE au niveau requête
   ✓ RLS Policies sur les tables
   ✓ Pas d'accès aux données non-autorisées

5. HTTPS (Recommandé en Production)
   ✓ Chiffrement des tokens
   ✓ Protection des credentials
   ✓ Prévention MITM
```

### Performance

```
Opération                    Temps attendu  Cible
─────────────────────────────────────────────────
Charger le hub RBAC         < 500ms        ✓
Import petite matrice       < 2s           ✓
Afficher statut RBAC        < 1s           ✓
Requête PostgREST standard  < 200ms        ✓
Authentification JWT         < 100ms        ✓

### Hiérarchie des Rôles (Niveaux)

Le système utilise un champ `level` (1, 2 ou 3) pour définir une hiérarchie au sein de chaque catégorie :

| Catégorie | Niveau 1 (Opérationnel) | Niveau 2 (Superviseur) | Niveau 3 (Coordination) |
|-----------|-------------------------|------------------------|-------------------------|
| **ADMIN** | `Admin_L1` | `Admin_L2` | `ADMIN` |
| **MRV**   | `MRV_L1`, `MRV` | `MRV_L2` | `MRV_L3` |
| **EXPANSION** | `Expansion_L1` | `Expansion_L2` | `EXPANSION` |
| **AUTRES** | `OP_SAISIE`, `QUANTIFICATEUR` | `FINANCE` | - |
```

---

**Diagrammes créés:** 2024
**Architecture v1.0**
**Statut:** Production Ready