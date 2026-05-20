# 📋 Guide d'Utilisation - Interface de Consultation des Logs d'Audit

## Aperçu

L'interface de consultation des logs d'audit permet aux administrateurs et utilisateurs authentifiés de:
- Consulter l'historique complet de toutes les modifications effectuées dans le système
- Rechercher et filtrer les logs par table, opération, utilisateur ou date
- Voir les détails complets d'une modification (avant/après)
- Suivre l'intégrité des données avec les hash d'audit

## Accès à l'Interface

### Méthode 1: Via le panneau d'administration Django
1. Connectez-vous à l'admin Django (`/admin/`)
2. Cherchez "Audit Log" dans le panneau de gauche
3. Cliquez pour voir la liste des logs

### Méthode 2: Accès direct
- **Liste des logs**: `http://votre-domaine/admin/audit-logs/`
- **Détail d'un log**: `http://votre-domaine/admin/audit-logs/<id>/`

### Méthode 3: Via l'API
- **Récupérer les logs en JSON**: `GET /api/audit-logs/`

## Fonctionnalités

### 1. Filtrage des Logs

#### Recherche Globale
Permet une recherche dans tous les champs:
- Nom de la table
- ID de l'enregistrement
- ID utilisateur
- Type d'opération

Exemple: Rechercher "membres" trouvera tous les logs concernant la table "membre"

#### Filtres Spécifiques

**Par Table**: 
- Sélectionnez une table spécifique (ex: "bosquet_baseline", "membre", etc.)
- Laissez vide pour voir toutes les tables

**Par Opération**:
- `CREATE`: Création d'un nouvel enregistrement
- `UPDATE`: Modification d'un enregistrement existant
- `DELETE`: Suppression d'un enregistrement
- `INSERT`: Insertion de nouvelles données

**Par Utilisateur**:
- Entrez l'ID utilisateur qui a effectué l'action
- Laissez vide pour voir toutes les modifications

### 2. Affichage des Résultats

#### Tableau Principal
Le tableau affiche les colonnes suivantes pour chaque log:

| Colonne | Description |
|---------|-------------|
| ID | Identifiant unique du log |
| Table | Table concernée par la modification |
| Opération | Type d'opération (avec badge coloré) |
| Record ID | ID de l'enregistrement modifié |
| Utilisateur | ID de l'utilisateur ayant effectué l'action |
| Date/Heure | Timestamp de l'action (format JJ/MM/AAAA HH:mm:ss) |
| Actions | Lien pour voir les détails |

#### Badges d'Opération
- 🟢 **CREATE/INSERT** (vert): Nouvelle création
- 🟡 **UPDATE** (jaune): Modification
- 🔴 **DELETE** (rouge): Suppression

### 3. Vue Détaillée

Cliquez sur "👁️ Détail" pour voir les informations complètes d'un log:

#### Section Informations Générales
- **ID du Log**: Clé unique de ce log
- **Table affectée**: Nom de la table modifiée
- **Opération**: Type d'action effectuée
- **ID de l'enregistrement**: Identifiant du record modifié
- **Utilisateur**: Qui a effectué l'action
- **Date/Heure**: Quand l'action a eu lieu
- **Hash**: Vérification d'intégrité (hash cryptographique)

#### Section Données Modifiées
Affiche la comparaison avant/après pour les modifications:

**Pour UPDATE**:
- ❌ **Données Anciennes**: État avant modification
- ✅ **Nouvelles Données**: État après modification

**Pour DELETE**:
- 🗑️ **Données Supprimées**: Les données qui ont été supprimées

**Pour INSERT/CREATE**:
- 📥 **Données Insérées**: Les nouvelles données ajoutées

## Pagination

- Par défaut: **50 logs par page**
- Navigation: Première | Précédente | [Numéros de pages] | Suivante | Dernière
- Filtres conservés lors de la navigation

## API REST

### Endpoint: GET /api/audit-logs/

#### Paramètres de Requête

```
GET /api/audit-logs/?table_name=bosquet&operation=UPDATE&user_id=user123&days=7&limit=100
```

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `table_name` | string | Filtre par table (contient) | - |
| `operation` | string | Type d'opération (exact) | - |
| `user_id` | string | ID utilisateur (contient) | - |
| `days` | integer | Nombre de jours en arrière | 30 |
| `limit` | integer | Nombre maximum de résultats | 100 |

#### Réponse Exemple

```json
{
  "count": 42,
  "days": 7,
  "limit": 100,
  "timestamp": "2026-05-19T10:30:45.123456Z",
  "data": [
    {
      "id": 1,
      "table_name": "bosquet_baseline",
      "operation": "UPDATE",
      "record_id": "uuid-12345",
      "user_id": "user123",
      "action_time": "2026-05-19T09:15:30.123456Z",
      "old_data": {"nom_proprietaire": "Jean Dupont", "surface": 2.5},
      "new_data": {"nom_proprietaire": "Jean Dupont", "surface": 3.0},
      "current_hash": "abc123..."
    }
  ]
}
```

#### Exemples cURL

**Récupérer tous les logs des 30 derniers jours**:
```bash
curl "http://localhost/api/audit-logs/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Filtrer par table (dernière semaine)**:
```bash
curl "http://localhost/api/audit-logs/?table_name=membre&days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Récupérer les suppressions d'un utilisateur**:
```bash
curl "http://localhost/api/audit-logs/?operation=DELETE&user_id=operateur1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Permissions

### Accès à la Page Web
- ✅ Utilisateurs authentifiés
- ✅ Administrateurs (super-utilisateurs)

### Accès à l'Admin Django
- ✅ Utilisateurs ayant la permission `view_auditlog`
- ✅ Super-utilisateurs
- ❌ Modification/Suppression pour les utilisateurs normaux

### Accès à l'API
- ✅ Administrateurs uniquement (`IsAdminUser`)
- ❌ Utilisateurs normaux

## Cas d'Usage Courants

### 1. Auditer les Modifications d'un Utilisateur
```
1. Aller à /admin/audit-logs/
2. Entrer l'ID utilisateur dans le filtre "Utilisateur"
3. Cliquer sur "Rechercher"
```

### 2. Trouver Toutes les Suppressions du Mois
```
1. Filtrer par Opération: "DELETE"
2. Rechercher sur une période (manuellement par date)
3. Examiner chaque log pour les détails
```

### 3. Suivre les Modifications d'un Enregistrement
```
1. Utiliser la recherche globale avec l'ID de l'enregistrement
2. Tous les logs concernant ce record s'affichent
3. Parcourir l'historique complet des modifications
```

### 4. Vérifier l'Intégrité des Données
```
1. Consulter les hash (current_hash et previous_hash)
2. S'assurer que les modifications sont cohérentes
3. Détecter les anomalies ou modifications non autorisées
```

## Informations Techniques

### Modèle AuditLog
Le modèle stocke les champs suivants:

| Champ | Type | Description |
|-------|------|-------------|
| id | BigAutoField | Clé primaire auto-incrémentée |
| table_name | TextField | Nom de la table modifiée |
| operation | TextField | type d'opération (INSERT, UPDATE, DELETE, etc.) |
| record_id | TextField | Identifiant de l'enregistrement affecté |
| user_id | TextField | ID de l'utilisateur (peut être NULL pour les actions système) |
| action_time | DateTimeField | Timestamp UTC de l'action |
| old_data | JSONField | Données avant la modification |
| new_data | JSONField | Données après la modification |
| previous_hash | TextField | Hash SHA256 du state précédent |
| current_hash | TextField | Hash SHA256 du state actuel |

### Vues Django

#### `audit_logs_view`
- **URL**: `/admin/audit-logs/`
- **Méthode**: GET
- **Permission**: login_required
- **Retourne**: Page HTML avec liste paginée

#### `audit_log_detail_view`
- **URL**: `/admin/audit-logs/<id>/`
- **Méthode**: GET
- **Permission**: login_required
- **Retourne**: Page HTML avec détails du log

#### `audit_logs_api_view`
- **URL**: `/api/audit-logs/`
- **Méthode**: GET
- **Permission**: IsAdminUser
- **Retourne**: JSON

### Admin Django
L'interface d'administration Django pour AuditLog offre:
- ✅ Lecture complète de tous les logs
- ✅ Recherche et filtrage avancés
- ✅ Tri par date, table, opération
- ✅ Affichage JSON des données modifiées
- ❌ Aucune modification possible (lecture seule)
- ❌ Suppression réservée aux superusers

## Limitations et Notes

1. **Données Historiques**: Les logs sont créés au moment de l'action. Les logs antérieurs à l'implémentation du système d'audit ne seront pas disponibles.

2. **Performance**: Avec de grandes quantités de logs (>100 000), les performances peuvent être dégradées. Utilisez des filtres pour réduire le jeu de résultats.

3. **Stockage**: Les données JSON (old_data, new_data) peuvent être volumineuses. Planifiez l'archivage des anciens logs.

4. **Hash Verification**: Les hash SHA256 servent à vérifier l'intégrité des données. Ne pas modifier les hash manuellement.

5. **Timezone**: Tous les timestamps sont en UTC. L'interface les affiche dans le fuseau horaire du serveur.

## Dépannage

### Question: Je ne vois pas les logs
**Réponse**: 
- Assurez-vous d'être connecté
- Vérifiez que le système d'audit est activé
- L'application doit être en production pour générer des logs

### Question: Le détail du log ne s'affiche pas
**Réponse**:
- Le log a peut-être été supprimé
- Vérifiez l'ID du log dans l'URL
- Consultez les autres logs pour confirmer le système fonctionne

### Question: Comment exporter les logs?
**Réponse**:
- Utilisez l'API `/api/audit-logs/` pour récupérer les données en JSON
- Les données peuvent ensuite être exporter en CSV via un script

## Support et Maintenance

Pour plus d'informations:
- Consultez la documentation Django: https://docs.djangoproject.com/
- Consultez la documentation DRF: https://www.django-rest-framework.org/

---

**Dernière mise à jour**: 19 mai 2026

