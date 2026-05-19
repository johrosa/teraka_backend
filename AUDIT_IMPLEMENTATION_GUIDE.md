# Guide d'implémentation de l'audit log Teraka

Ce document explique comment capturer les utilisateurs Django dans les triggers PostgreSQL pour l'audit complet du système.

## 1. Fonctionnement de la capture utilisateur
L'architecture Teraka utilise Django pour l'authentification et PostgREST pour l'API. PostgREST expose automatiquement les informations du JWT dans la session PostgreSQL.

La capture du `username` Django s'effectue via :
`current_setting('request.jwt.claims', true)::json->>'username'`

Le système prévoit un fallback sur `current_user` pour les actions effectuées directement en SQL ou via l'interface d'administration standard de Django.

## 2. Contenu de la solution (final_audit_solution.sql)
Le script SQL fournit une solution clé en main :
- **Table `audit_log`** : Stockage sécurisé des opérations avec une chaîne de hachage SHA-256 pour garantir l'immutabilité.
- **Trigger `audit_trigger`** : Fonction générique capable de gérer n'importe quelle table en spécifiant sa clé primaire.
- **Vues d'analyse** :
    - `audit_readable_view` : Historique lisible des actions.
    - `audit_diff_view` : Focus sur les changements précis de valeurs lors des UPDATE.
- **Vérification d'intégrité** :
    - `verify_audit_chain()` : Fonction SQL pour valider que les logs n'ont pas été altérés.

## 3. Déploiement sur de nouvelles tables
Pour auditer une table, créez le trigger en passant le nom de la colonne PK en argument :

```sql
-- Exemple pour la table 'membre' (PK: uuid_membre)
CREATE TRIGGER audit_membre
AFTER INSERT OR UPDATE OR DELETE ON membre
FOR EACH ROW EXECUTE FUNCTION audit_trigger('uuid_membre');
```

## 4. Consultation des logs
```sql
-- Voir les dernières actions
SELECT * FROM audit_readable_view ORDER BY date_action DESC;

-- Vérifier si les logs sont valides (non corrompus)
SELECT * FROM verify_audit_chain() WHERE is_valid = false;
```
