-- Script de secours robuste pour aligner une base de données existante
-- Gère l'ajout de la colonne 'level' et les contraintes NOT NULL

BEGIN;

-- 1. Ajout des colonnes Auth manquantes à la table users
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_staff BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS date_joined TIMESTAMPTZ DEFAULT now();

-- 2. Correction du type pour django_admin_log (BigInt -> UUID)
-- Évite l'erreur: "operator does not exist: bigint = uuid"
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='django_admin_log' AND column_name='user_id' AND data_type='bigint'
    ) THEN
        -- Supprimer la contrainte de clé étrangère pointant vers users(id)
        ALTER TABLE django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_users_id;

        -- Convertir en UUID en utilisant uuid_user
        ALTER TABLE django_admin_log
            ALTER COLUMN user_id TYPE UUID
            USING (SELECT uuid_user FROM users WHERE users.id = django_admin_log.user_id);

        -- Recréer la contrainte pointant vers users(uuid_user)
        ALTER TABLE django_admin_log
            ADD CONSTRAINT django_admin_log_user_id_fk_users_uuid_user
            FOREIGN KEY (user_id) REFERENCES users(uuid_user)
            DEFERRABLE INITIALLY DEFERRED;
    END IF;
END $$;

-- 3. Création des tables de liaison nécessaires pour PermissionsMixin
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

-- 4. Création/Mise à jour de la table core_role
CREATE TABLE IF NOT EXISTS core_role (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Gestion robuste de la colonne 'level'
DO $$
BEGIN
    -- Ajouter la colonne level si elle n'existe pas (nullable au début)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='core_role' AND column_name='level') THEN
        ALTER TABLE core_role ADD COLUMN level INTEGER;
    END IF;
END $$;

-- Mettre à jour les lignes existantes avec une valeur par défaut
UPDATE core_role SET level = 1 WHERE level IS NULL;

-- Mettre la valeur par défaut pour les futures insertions
ALTER TABLE core_role ALTER COLUMN level SET DEFAULT 1;

-- 5. Initialisation des rôles par défaut
-- Utilisation d'une table temporaire pour l'UPSERT
CREATE TEMP TABLE tmp_roles (code VARCHAR(64), description VARCHAR(255), level INTEGER);
INSERT INTO tmp_roles (code, description, level) VALUES
    ('Expansion_L1', 'Expansion L1 - Création seulement', 1),
    ('Expansion_L2', 'Expansion L2 - Lecture + Modification', 2),
    ('EXPANSION', 'Expansion - Niveau 3 (Coordination)', 3),
    ('MRV_L1', 'MRV L1 - Lecture seule', 1),
    ('MRV_L2', 'MRV L2 - Lecture + Modification', 2),
    ('MRV_L3', 'MRV L3 - Lecture + Modification + Validation', 3),
    ('MRV', 'MRV - Base (Niveau 1)', 1),
    ('Admin_L1', 'Admin L1 - Lecture + Modification', 1),
    ('Admin_L2', 'Admin L2 - Lecture + Modification + Suppression', 2),
    ('ADMIN', 'Administrateur - Niveau 3 (Global)', 3),
    ('FINANCE', 'Finance (Niveau 2)', 2),
    ('OP_SAISIE', 'Opérateur de Saisie (Niveau 1)', 1),
    ('QUANTIFICATEUR', 'Quantificateur (Niveau 1)', 1);

INSERT INTO core_role (code, description, level)
SELECT code, description, level FROM tmp_roles
ON CONFLICT (code) DO UPDATE SET
    description = EXCLUDED.description,
    level = EXCLUDED.level;

DROP TABLE tmp_roles;

-- Appliquer la contrainte NOT NULL seulement après avoir rempli les données
ALTER TABLE core_role ALTER COLUMN level SET NOT NULL;

-- 6. Mise à jour de core_userrole
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

-- 7. Création de FieldMapping
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

-- 8. Enregistrement des migrations
INSERT INTO django_migrations (app, name, applied)
VALUES
    ('core', '0001_initial', now()),
    ('core', '0002_userrole_auditlog', now()),
    ('core', '0002b_userrole_safe', now()),
    ('core', '0003_merge_0002_userrole_auditlog_0002b_userrole_safe', now()),
    ('core', '0004_role_model', now()),
    ('core', '0005_fieldmapping', now()),
    ('core', '0006_alter_role_options_alter_userrole_options_role_level_and_more', now())
ON CONFLICT (app, name) DO NOTHING;

COMMIT;
