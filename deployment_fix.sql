-- Script de secours pour aligner une base de données existante avec le nouveau schéma
-- A utiliser si les migrations Django échouent en raison d'un état incohérent

BEGIN;

-- 1. Création sécurisée de la table Role
CREATE TABLE IF NOT EXISTS core_role (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Initialisation des rôles par défaut
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

-- 3. Mise à jour de core_userrole
-- Si la colonne 'role' (VARCHAR) existe encore, on la renomme pour la migrer vers FK
DO $$
BEGIN
    -- Si la colonne role existe et n'est pas une FK (type text/varchar)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='core_userrole' AND column_name='role'
        AND data_type IN ('text', 'character varying')
    ) THEN
        -- On ajoute la colonne temporaire pour la FK
        ALTER TABLE core_userrole ADD COLUMN IF NOT EXISTS role_id_new BIGINT;

        -- On mappe les anciens codes vers les IDs de la table Role
        UPDATE core_userrole ur
        SET role_id_new = r.id
        FROM core_role r
        WHERE ur.role = r.code;

        -- On supprime l'ancienne colonne et on renomme la nouvelle
        ALTER TABLE core_userrole DROP COLUMN role;
        ALTER TABLE core_userrole RENAME COLUMN role_id_new TO role_id;

        -- On ajoute la contrainte FK
        ALTER TABLE core_userrole
        ADD CONSTRAINT core_userrole_role_id_fk
        FOREIGN KEY (role_id) REFERENCES core_role(id);
    END IF;
END $$;

-- 4. Création de FieldMapping
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

-- 5. Enregistrement forcé des migrations pour éviter les erreurs NodeNotFoundError
INSERT INTO django_migrations (app, name, applied)
VALUES
    ('core', '0001_initial', now()),
    ('core', '0002_userrole_auditlog', now()),
    ('core', '0002b_userrole_safe', now()),
    ('core', '0003_merge_0002_userrole_auditlog_0002b_userrole_safe', now()),
    ('core', '0002_role_model', now()),
    ('core', '0003_fieldmapping', now())
ON CONFLICT (app, name) DO NOTHING;

COMMIT;
