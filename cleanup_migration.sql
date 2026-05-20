-- Script pour nettoyer l'enregistrement de migration et permettre de la re-appliquer

-- D'abord, vérifier l'état actuel
SELECT * FROM django_migrations WHERE app = 'core' AND name LIKE '0002%';

-- Supprimer l'enregistrement de migration s'il existe
DELETE FROM django_migrations WHERE app = 'core' AND name = '0002_userrole_auditlog';

-- Vérifier que c'est supprimé
SELECT * FROM django_migrations WHERE app = 'core' ORDER BY id DESC LIMIT 5;

-- Afficher toutes les migrations de core pour vérification
\echo '\n--- Migrations actuelles de core ---'
SELECT id, app, name, applied FROM django_migrations WHERE app = 'core' ORDER BY id;

