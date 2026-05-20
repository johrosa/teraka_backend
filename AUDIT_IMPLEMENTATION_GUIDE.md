# Guide d'implémentation de l'audit log et corrections Teraka

Ce document explique comment déployer le système d'audit complet et appliquer les corrections de schéma nécessaires.

## 1. Correction du bug UserRole
Si vous rencontrez l'erreur `column core_userrole.role does not exist`, exécutez le script suivant :
`psql -f fix_userrole_schema.sql`

## 2. Système d'audit (final_audit_solution.sql)
Le système d'audit capture l'identité des utilisateurs Django via les claims JWT de PostgREST.

### Fonctionnement
La capture s'effectue via :
`current_setting('request.jwt.claims', true)::json->>'username'`

### Déploiement
1. Exécutez `psql -f final_audit_solution.sql`.
2. Appliquez le trigger aux tables souhaitées :
```sql
CREATE TRIGGER audit_ma_table
AFTER INSERT OR UPDATE OR DELETE ON ma_table
FOR EACH ROW EXECUTE FUNCTION audit_trigger('nom_colonne_pk');
```

## 3. Import QGIS amélioré
La commande `import_qgis_data` supporte désormais un mode interactif pour résoudre les problèmes de mapping (notamment pour Mergin).

**Usage :**
`python manage.py import_qgis_data mon_projet.qgz --interactive`

Cela affichera un dialogue de mapping manuel si les couches ou les champs ne sont pas automatiquement reconnus.
