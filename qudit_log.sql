-- Create audit log table
CREATE TABLE audit_log (
    uuid          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name    TEXT        NOT NULL,
    operation     TEXT        NOT NULL, -- INSERT / UPDATE / DELETE
    record_id     TEXT,
    user_id       TEXT,
    action_time   TIMESTAMPTZ NOT NULL DEFAULT now(),

    old_data      JSONB,
    new_data      JSONB,

    previous_hash TEXT,
    current_hash  TEXT        NOT NULL
);


-- Create audit hash function
CREATE EXTENSION IF NOT EXISTS pgcrypto;

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

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS trigger AS $$
DECLARE
    v_prev_hash TEXT;
    v_record_id TEXT;
BEGIN
    SELECT current_hash
    INTO v_prev_hash
    FROM audit_log
    ORDER BY id DESC
    LIMIT 1;

    IF TG_OP = 'INSERT' THEN
        v_record_id := NEW.id::text;
        INSERT INTO audit_log (
            table_name, operation, record_id, user_name,
            old_data, new_data, previous_hash, current_hash
        )
        VALUES (
            TG_TABLE_NAME, TG_OP, v_record_id, current_user,
            NULL, to_jsonb(NEW), v_prev_hash,
            compute_audit_hash(TG_TABLE_NAME, TG_OP, v_record_id, NULL, to_jsonb(NEW), v_prev_hash)
        );
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        v_record_id := NEW.id::text;
        INSERT INTO audit_log (
            table_name, operation, record_id, user_id,
            old_data, new_data, previous_hash, current_hash
        )
        VALUES (
            TG_TABLE_NAME, TG_OP, v_record_id, current_user,
            to_jsonb(OLD), to_jsonb(NEW), v_prev_hash,
            compute_audit_hash(TG_TABLE_NAME, TG_OP, v_record_id, to_jsonb(OLD), to_jsonb(NEW), v_prev_hash)
        );
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        v_record_id := OLD.id::text;
        INSERT INTO audit_log (
            table_name, operation, record_id, user_id,
            old_data, new_data, previous_hash, current_hash
        )
        VALUES (
            TG_TABLE_NAME, TG_OP, v_record_id, current_user,
            to_jsonb(OLD), NULL, v_prev_hash,
            compute_audit_hash(TG_TABLE_NAME, TG_OP, v_record_id, to_jsonb(OLD), NULL, v_prev_hash)
        );
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Prevent manual modification of audit log
REVOKE INSERT, UPDATE, DELETE ON audit_log FROM PUBLIC;
REVOKE INSERT, UPDATE, DELETE ON audit_log FROM pg_read_all_data;
GRANT SELECT ON audit_log TO pg_read_all_data;

ALTER FUNCTION audit_trigger_function() OWNER TO postgres;

ALTER FUNCTION audit_trigger_function() SECURITY DEFINER;

CREATE OR REPLACE FUNCTION prevent_manual_edit()
RETURNS trigger AS
$$
BEGIN
    IF TG_OP IN ('UPDATE','DELETE') THEN
        RAISE EXCEPTION 'Audit log est en lecture seule';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_manual_update
BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW
EXECUTE FUNCTION prevent_manual_edit();


--Crate readable view
CREATE OR REPLACE VIEW audit_readable_view AS
SELECT
    id                       AS audit_id,
    action_time                  AS date_action,
    table_name                   AS table_cible,
    operation                    AS type_operation,
    record_id                    AS id_objet,
    user_id                    AS utilisateur,

    -- Données simplifiées
    old_data                     AS avant_modification,
    new_data                     AS apres_modification,

    previous_hash,
    current_hash,

    -- Vérification simple de continuité
    CASE
        WHEN previous_hash IS NULL THEN 'GENESIS'
        ELSE 'CHAINED'
    END AS chain_status
FROM audit_log
ORDER BY id;

-- Create difference view
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

-- Verify audit chain
CREATE OR REPLACE FUNCTION verify_audit_chain()
RETURNS TABLE (
    audit_id BIGINT,
    is_valid BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.current_hash =
        compute_audit_hash(
            a.table_name,
            a.operation,
            a.record_id,
            a.old_data,
            a.new_data,
            a.previous_hash
        ) AS is_valid
    FROM audit_log a;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM verify_audit_chain() WHERE is_valid = true;

-- Add audit trigger to tables
CREATE TRIGGER audit_commune
AFTER INSERT OR UPDATE OR DELETE
ON communes
FOR EACH ROW
EXECUTE FUNCTION audit_trigger();
