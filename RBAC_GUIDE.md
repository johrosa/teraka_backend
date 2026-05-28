# Guide RBAC Autonome - Teraka Platform

## 📋 Vue d'ensemble

Le système RBAC (Role-Based Access Control) de Teraka est maintenant accessible via **3 URLs autonomes** depuis l'interface d'administration Django.

### URLs disponibles

| URL | Accès | Description |
|-----|-------|-------------|
| `/admin/rbac/` | Administrateurs | 🏠 Hub central RBAC |
| `/admin/rbac/import/` | Administrateurs | 📥 Importer la matrice RBAC |
| `/admin/rbac/status/` | Administrateurs | 📊 Consulter le statut des permissions |
| `/admin/core/userrole/` | Administrateurs | 👤 Gérer les rôles des utilisateurs |

---

## 🏠 Hub Central RBAC (`/admin/rbac/`)

Le hub central est le point d'accès unique pour gérer toutes les permissions RBAC.

**Accès:** `http://localhost:8000/admin/rbac/`

### Fonctionnalités

1. **Gestion des rôles utilisateurs** 👤
   - Associer des rôles PostgreSQL aux utilisateurs Django
   - Voir l'historique des changements
   - Modifier les rôles existants

2. **Importer la matrice RBAC** 📥
   - Créer les rôles PostgreSQL
   - Réinitialiser les permissions
   - Appliquer une nouvelle matrice complète

3. **Consulter le statut RBAC** 📊
   - Voir tous les rôles configurés
   - Lister les tables sécurisées
   - Détails des permissions par rôle/table

4. **Dashboard Teraka** 📈
   - Vue d'ensemble statistique
   - Répartition des utilisateurs
   - Données géographiques

---

## 📥 Importer la matrice RBAC

### Accès
`http://localhost:8000/admin/rbac/import/`

### Processus d'import

1. **Préparer le fichier CSV/Excel**
   - Format: Première colonne = nom de table, colonnes suivantes = codes de permission
   - Codes autorisés:
     - `C` = Create (Créer)
     - `R` = Read (Lire)
     - `U` = Update (Modifier)
     - `D` = Delete (Supprimer)
     - `V` = Validate (Valider)
     - `-` = Aucun accès

2. **Exemple de matrice**
   ```
   Table,Expansion_L1,Expansion_L2,MRV_L1,MRV_L2,MRV_L3
   sites,C--,-,R,RU,RU
   data_points,-,RU,R,RU,RU
   projects,-,RU,R,RU,RUD
   validations,-,-,-,RU,RUD
   ```

3. **Télécharger le fichier**
   - Accédez à `/admin/rbac/import/`
   - Cliquez sur "Choisir un fichier"
   - Sélectionnez votre fichier CSV ou Excel

4. **Appliquer les modifications**
   - Cliquez sur "Importer"
   - Vérifiez les résultats
   - Les rôles PostgreSQL sont créés automatiquement

---

## 📊 Consulter le statut RBAC

### Accès
`http://localhost:8000/admin/rbac/status/`

### Informations disponibles

- **Rôles PostgreSQL configurés**
  - Liste de tous les rôles
  - Utilisateurs assignés à chaque rôle

- **Tables sécurisées**
  - Liste des tables avec RLS activé
  - Statut des politiques de sécurité

- **Permissions détaillées**
  - Permissions par rôle et par table
  - Affichage des codes (C/R/U/D/V)

---

## 👤 Gérer les rôles des utilisateurs

### Accès
`http://localhost:8000/admin/core/userrole/`

### Actions disponibles

1. **Créer une assignation de rôle**
   - Sélectionner un utilisateur Django
   - Choisir un rôle PostgreSQL
   - Définir la date d'activation

2. **Modifier une assignation**
   - Changer le rôle d'un utilisateur
   - Mettre à jour la date d'activation
   - Voir l'historique des changements

3. **Supprimer une assignation**
   - Retirer un utilisateur d'un rôle
   - Les permissions sont révoquées automatiquement

---

## 🔒 Rôles PostgreSQL configurés

Le système RBAC utilise les rôles PostgreSQL suivants avec une hiérarchie par niveau :

| Rôle | Niveau | Description |
|------|--------|-------------|
| `ADMIN` | 3 | Administrateur Global |
| `Admin_L1` | 1 | Admin L1 - Lecture + Modification |
| `Admin_L2` | 2 | Admin L2 - Lecture + Modification + Suppression |
| `EXPANSION` | 1 | Expansion - Général |
| `Expansion_L1` | 1 | Expansion L1 - Création seulement |
| `Expansion_L2` | 2 | Expansion L2 - Lecture + Modification |
| `MRV` | 1 | MRV - Général |
| `MRV_L1` | 1 | MRV L1 - Lecture seule |
| `MRV_L2` | 2 | MRV L2 - Lecture + Modification |
| `MRV_L3` | 3 | MRV L3 - Lecture + Modification + Validation |
| `FINANCE` | 2 | Finance |
| `OP_SAISIE` | 1 | Opérateur de Saisie |
| `QUANTIFICATEUR` | 1 | Quantificateur |

---

## 🔗 Intégration avec PostgREST

### Fonctionnement

1. **Utilisateur se connecte via `/api/login/`**
   - Identifiants: username/password
   - Reçoit un token JWT incluant son rôle PostgreSQL et son **niveau (level)**

2. **Requête à `/api/data/*` avec le token**
   - PostgREST exécute avec les permissions du rôle.
   - Les claims `role` et `level` sont disponibles dans la session PostgreSQL.
   - Accès refusé (403) si permissions insuffisantes.

3. **Politique de sécurité au niveau base de données**
   - Aucune données sensibles exposées au-delà des droits du rôle

### Exemple de flux

```
1. POST /api/login/
   → JWT Token: eyJhbGc...include "Expansion_L2"...

2. GET /api/data/sites?select=id,name
   Header: Authorization: Bearer eyJhbGc...
   → PostgREST: SET ROLE 'Expansion_L2'
   → Retourne seulement les sites autorisés

3. DELETE /api/data/projects/123
   Header: Authorization: Bearer eyJhbGc...
   → PostgREST: SET ROLE 'Expansion_L2'
   → Erreur 403: Rôle n'a pas permission DELETE
```

---

## 🚀 Workflow typique d'administration

### Scénario: Ajouter un nouveau collaborateur

1. **Créer l'utilisateur Django**
   - Admin > Utilisateurs > Ajouter utilisateur
   - Définir username/email/mot de passe

2. **Assigner un rôle RBAC**
   - Aller à `/admin/rbac/`
   - Cliquer "Gestion des rôles utilisateurs"
   - Ajouter assignation: utilisateur + rôle

3. **Vérifier l'accès**
   - Aller à `/admin/rbac/status/`
   - Consulter les permissions du nouvel utilisateur

4. **L'utilisateur peut se connecter**
   - Accès API: `POST /api/login/` avec ses identifiants
   - Accès données: `GET /api/data/*` avec ses permissions

---

## 🛠️ Dépannage

### Problème: Utilisateur n'a pas accès aux données

**Solutions:**
1. Vérifier que l'utilisateur est assigné à un rôle
   - `/admin/rbac/` > Gestion des rôles utilisateurs
   - Rechercher l'utilisateur

2. Vérifier le statut du rôle
   - `/admin/rbac/status/`
   - Voir les permissions du rôle

3. Vérifier l'import de la matrice
   - `/admin/rbac/import/`
   - Réimporter si nécessaire

### Problème: Rôle introuvable dans PostgREST

**Solutions:**
1. Réimporter la matrice RBAC
   - `/admin/rbac/import/`

2. Vérifier la connexion PostgreSQL
   - Les rôles doivent être créés en base de données

### Problème: Token JWT invalide

**Solutions:**
1. Vérifier la clé secrète Django
   - Setting: `SECRET_KEY` dans `settings.py`

2. Vérifier l'expiration du token
   - Détail: `settings.py` > `SIMPLE_JWT`

---

## 📞 Support & Contact

Pour toute question ou problème:
- Consulter la [documentation PostgREST](https://postgrest.org)
- Consulter la [documentation Django](https://docs.djangoproject.com)
- Contacter l'équipe DevOps Teraka

---

**Dernière mise à jour:** 2024
**Version:** 1.0
**Plateforme:** Teraka Django Backend