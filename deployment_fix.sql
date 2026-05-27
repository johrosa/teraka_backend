-- Script de secours pour aligner une base de données existante avec le nouveau schéma

BEGIN;

-- 1. Ajout des colonnes Auth manquantes à la table users
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_staff BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS date_joined TIMESTAMPTZ DEFAULT now();

-- 2. Création des tables de liaison nécessaires pour PermissionsMixin
-- Django s'attend par défaut à core_users_groups/permissions pour le modèle Users de l'app core
CREATE TABLE IF NOT EXISTS core_users_groups (
    id BIGSERIAL PRIMARY KEY,
    users_id UUID NOT NULL REFERENCES users(uuid_user) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE(users_id, group_id)
);

CREATE TABLE IF NOT EXISTS core_users_user_permissions (
    id BIGSERIAL PRIMARY KEY,
    users_id UUID NOT NULL REFERENCES users(uuid_user) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(users_id, permission_id)
);

-- 3. Création sécurisée de la table Role
CREATE TABLE IF NOT EXISTS core_role (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Initialisation des rôles par défaut
INSERT INTO core_role (code, description)
VALUES
    ('Expansion_L1', 'Expansion L1 - Création seulement'),
    ('Expansion_L2', 'Expansion L2 - Lecture + Modification'),
    ('MRV_L1', 'MRV L1 - Lecture seule'),
    ('MRV_L2', 'MRV L2 - Lecture + Modification'),
    ('MRV_L3', 'MRV L3 - Lecture + Modification + Validation'),
    ('Admin_L1', 'Admin L1 - Lecture + Modification'),
    ('Admin_L2', 'Admin L2 - Lecture + Modification + Suppression')
ON CONFLICT (code) DO NOTHING;

-- 5. Mise à jour de core_userrole
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='core_userrole' AND column_name='role'
        AND data_type IN ('text', 'character varying')
    ) THEN
        ALTER TABLE core_userrole ADD COLUMN IF NOT EXISTS role_id_new BIGINT;
        UPDATE core_userrole ur SET role_id_new = r.id FROM core_role r WHERE ur.role = r.code;
        ALTER TABLE core_userrole DROP COLUMN role;
        ALTER TABLE core_userrole RENAME COLUMN role_id_new TO role_id;
        ALTER TABLE core_userrole ADD CONSTRAINT core_userrole_role_id_fk FOREIGN KEY (role_id) REFERENCES core_role(id);
    END IF;
END $$;

-- 6. Création de FieldMapping
CREATE TABLE IF NOT EXISTS core_fieldmapping (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(128) NOT NULL,
    field_name VARCHAR(128) NOT NULL,
    source_field_name VARCHAR(128) NOT NULL,
    comment TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(model_name, field_name)
);

-- 7. Enregistrement forcé des migrations (SANS dépendre de l'index UNIQUE)
INSERT INTO django_migrations (app, name, applied)
SELECT d.app, d.name, d.applied
FROM (VALUES
    ('core', '0001_initial', now()),
    ('core', '0002_userrole_auditlog', now()),
    ('core', '0002b_userrole_safe', now()),
    ('core', '0003_merge_0002_userrole_auditlog_0002b_userrole_safe', now()),
    ('core', '0004_role_model', now()),
    ('core', '0005_fieldmapping', now())
) AS d(app, name, applied)
WHERE NOT EXISTS (
    SELECT 1 FROM django_migrations m
    WHERE m.app = d.app AND m.name = d.name
);

COMMIT;
