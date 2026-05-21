# Guide d'implémentation de l'audit log et corrections Teraka

Ce document explique comment déployer le système d'audit complet et gérer les rôles utilisateurs.

## 1. Gestion des rôles (UserRole)
Le système a été mis à jour pour utiliser les **Groupes Django** au lieu d'une colonne dédiée dans la base de données. Cela permet d'éviter l'erreur `column core_userrole.role does not exist` tout en conservant l'interface d'administration habituelle.

Aucune action SQL n'est requise pour cette partie, les changements sont gérés par le code Django.

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
