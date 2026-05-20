-- ============================================================================
-- SYSTEME D'AUDIT COMPLET POUR TERAKA PLATFORM
-- Capture les utilisateurs Django via PostgREST (JWT)
-- ============================================================================

-- 1. Extension et Table audit_log
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS audit_log (
    id            BIGSERIAL PRIMARY KEY,
    uuid          UUID UNIQUE DEFAULT gen_random_uuid(),
    table_name    TEXT        NOT NULL,
    operation     TEXT        NOT NULL, -- INSERT / UPDATE / DELETE
    record_id     TEXT,
    user_id       TEXT, -- Contiendra le username Django (via JWT) ou l'utilisateur DB
    action_time   TIMESTAMPTZ NOT NULL DEFAULT now(),

    old_data      JSONB,
    new_data      JSONB,

    previous_hash TEXT,
    current_hash  TEXT        NOT NULL
);

-- 2. Fonction de hachage pour l'intégrité de la chaîne
CREATE OR REPLACE FUNCTION compute_audit_hash(
    p_table TEXT,
    p_op TEXT,
    p_record_id TEXT,
    p_old JSONB,
    p_new JSONB,
    p_prev_hash TEXT
)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(
        digest(
            coalesce(p_table,'') ||
            coalesce(p_op,'') ||
            coalesce(p_record_id,'') ||
            coalesce(p_old::text,'') ||
            coalesce(p_new::text,'') ||
            coalesce(p_prev_hash,''),
            'sha256'
        ),
        'hex'
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 3. Fonction de trigger principale
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS trigger AS $$
DECLARE
    v_prev_hash TEXT;
    v_record_id TEXT;
    v_user_id TEXT;
    v_pk_column TEXT := coalesce(TG_ARGV[0], 'id'); -- PK par défaut
BEGIN
    -- CAPTURE DE L'UTILISATEUR DJANGO
    -- PostgREST expose les claims du JWT dans 'request.jwt.claims'
    -- Le second argument 'true' évite une erreur si la variable n'est pas définie
    v_user_id := current_setting('request.jwt.claims', true)::json->>'username';

    -- Fallback sur l'utilisateur DB courant (admin Django, psql, etc.)
    IF v_user_id IS NULL THEN
        v_user_id := current_user;
    END IF;

    -- Récupération du hash précédent
    SELECT current_hash INTO v_prev_hash FROM audit_log ORDER BY id DESC LIMIT 1;

    -- Identification de l'ID de l'enregistrement
    IF TG_OP = 'DELETE' THEN
        v_record_id := to_jsonb(OLD) ->> v_pk_column;
    ELSE
        v_record_id := to_jsonb(NEW) ->> v_pk_column;
    END IF;

    -- Enregistrement du log
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, record_id, user_id, old_data, new_data, previous_hash, current_hash)
        VALUES (TG_TABLE_NAME, TG_OP, v_record_id, v_user_id, NULL, to_jsonb(NEW), v_prev_hash,
                compute_audit_hash(TG_TABLE_NAME, TG_OP, v_record_id, NULL, to_jsonb(NEW), v_prev_hash));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, user_id, old_data, new_data, previous_hash, current_hash)
        VALUES (TG_TABLE_NAME, TG_OP, v_record_id, v_user_id, to_jsonb(OLD), to_jsonb(NEW), v_prev_hash,
                compute_audit_hash(TG_TABLE_NAME, TG_OP, v_record_id, to_jsonb(OLD), to_jsonb(NEW), v_prev_hash));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, user_id, old_data, new_data, previous_hash, current_hash)
        VALUES (TG_TABLE_NAME, TG_OP, v_record_id, v_user_id, to_jsonb(OLD), NULL, v_prev_hash,
                compute_audit_hash(TG_TABLE_NAME, TG_OP, v_record_id, to_jsonb(OLD), NULL, v_prev_hash));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. Sécurité et intégrité
CREATE OR REPLACE FUNCTION prevent_manual_edit()
RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('UPDATE','DELETE') THEN
        RAISE EXCEPTION 'Audit log est en lecture seule';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_manual_update ON audit_log;
CREATE TRIGGER prevent_manual_update
BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_manual_edit();

-- Droits d'accès
REVOKE ALL ON audit_log FROM PUBLIC;
GRANT SELECT ON audit_log TO pg_read_all_data;
-- On autorise les rôles PostgREST à déclencher le trigger (via l'insertion indirecte)
-- Note: SECURITY DEFINER permet au trigger de s'exécuter avec les droits du propriétaire de la fonction (postgres)

-- 5. Vues de lecture
CREATE OR REPLACE VIEW audit_readable_view AS
SELECT
    id                       AS audit_id,
    action_time              AS date_action,
    table_name               AS table_cible,
    operation                AS type_operation,
    record_id                AS id_objet,
    user_id                  AS utilisateur,
    old_data                 AS avant_modification,
    new_data                 AS apres_modification,
    previous_hash,
    current_hash,
    CASE WHEN previous_hash IS NULL THEN 'GENESIS' ELSE 'CHAINED' END AS chain_status
FROM audit_log
ORDER BY id;

CREATE OR REPLACE VIEW audit_diff_view AS
SELECT
    a.id,
    a.action_time,
    a.table_name,
    a.operation,
    a.record_id,
    a.user_id,
    jsonb_object_keys(a.new_data) AS champ_modifie,
    a.old_data -> jsonb_object_keys(a.new_data) AS valeur_avant,
    a.new_data -> jsonb_object_keys(a.new_data) AS valeur_apres
FROM audit_log a
WHERE a.operation = 'UPDATE';

-- 6. Fonction de vérification de l'intégrité
CREATE OR REPLACE FUNCTION verify_audit_chain()
RETURNS TABLE (
    audit_id BIGINT,
    is_valid BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.current_hash = compute_audit_hash(a.table_name, a.operation, a.record_id, a.old_data, a.new_data, a.previous_hash) AS is_valid
    FROM audit_log a
    ORDER BY a.id;
END;
$$ LANGUAGE plpgsql;

-- 7. Application du trigger sur 'communes' (PK: uuid_com)
DROP TRIGGER IF EXISTS audit_commune ON communes;
CREATE TRIGGER audit_commune
AFTER INSERT OR UPDATE OR DELETE ON communes
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
