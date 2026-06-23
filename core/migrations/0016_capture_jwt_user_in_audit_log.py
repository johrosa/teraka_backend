"""Capture PostgREST JWT user UUIDs in audit_log.changed_by."""
from django.db import migrations


sql = r"""
ALTER TABLE public.audit_log
    ADD COLUMN IF NOT EXISTS event_date date;

UPDATE public.audit_log
SET event_date = event_time::date
WHERE event_date IS NULL;

ALTER TABLE public.audit_log
    ALTER COLUMN event_date SET DEFAULT CURRENT_DATE;

DROP VIEW IF EXISTS public.audit_log_view;

CREATE OR REPLACE FUNCTION public.audit_log_trigger() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    payload text;
    p_hash text;
    new_row jsonb;
    computed_hash text;
    actor text;
    jwt_claims jsonb;
BEGIN
    -- avoid recursion
    IF TG_TABLE_NAME = 'audit_log' THEN
        RETURN NULL;
    END IF;

    IF (TG_OP = 'DELETE') THEN
        new_row := to_jsonb(OLD);
    ELSE
        new_row := to_jsonb(NEW);
    END IF;

    SELECT row_hash INTO p_hash FROM public.audit_log
      WHERE schema_name = TG_TABLE_SCHEMA AND table_name = TG_TABLE_NAME
      ORDER BY id DESC LIMIT 1;

    BEGIN
        jwt_claims := nullif(current_setting('request.jwt.claims', true), '')::jsonb;
    EXCEPTION WHEN others THEN
        jwt_claims := NULL;
    END;

    -- Prefer an authenticated application/JWT actor; fall back to the DB role.
    actor := coalesce(
        nullif(nullif(current_setting('app.audit_user', true), ''), 'anonymous'),
        nullif(current_setting('request.jwt.claim.user_id', true), ''),
        nullif(jwt_claims ->> 'user_id', ''),
        nullif(current_setting('request.jwt.claim.sub', true), ''),
        nullif(jwt_claims ->> 'sub', ''),
        current_user
    );

    payload := jsonb_build_object(
        'op', TG_OP,
        'schema', TG_TABLE_SCHEMA,
        'table', TG_TABLE_NAME,
        'data', new_row,
        'txid', txid_current(),
        'actor', actor
    )::text;

    computed_hash := encode(digest(coalesce(p_hash,'') || payload || now()::text, 'sha256'), 'hex');

    INSERT INTO public.audit_log(schema_name, table_name, operation, row_data, changed_by, txid, prev_hash, row_hash)
    VALUES (TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, new_row, actor, txid_current(), p_hash, computed_hash);

    RETURN NULL;
END;
$$ SECURITY DEFINER;

CREATE OR REPLACE VIEW public.audit_log_view AS
SELECT
  a.id,
  a.event_date,
  a.event_time,
  a.schema_name,
  a.table_name,
  a.operation,
  a.row_data,
  a.changed_by,
  u.email AS changed_by_email,
  a.txid,
  a.prev_hash,
  a.row_hash
FROM public.audit_log a
LEFT JOIN public.users u ON u.uuid_user::text = a.changed_by;
"""


reverse_sql = r"""
DROP VIEW IF EXISTS public.audit_log_view;

CREATE OR REPLACE FUNCTION public.audit_log_trigger() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    payload text;
    p_hash text;
    new_row jsonb;
    computed_hash text;
    actor text;
BEGIN
    -- avoid recursion
    IF TG_TABLE_NAME = 'audit_log' THEN
        RETURN NULL;
    END IF;

    IF (TG_OP = 'DELETE') THEN
        new_row := to_jsonb(OLD);
    ELSE
        new_row := to_jsonb(NEW);
    END IF;

    SELECT row_hash INTO p_hash FROM public.audit_log
      WHERE schema_name = TG_TABLE_SCHEMA AND table_name = TG_TABLE_NAME
      ORDER BY id DESC LIMIT 1;

    -- prefer application-provided actor; fall back to DB user
    actor := coalesce(current_setting('app.audit_user', true), current_user);

    payload := jsonb_build_object(
        'op', TG_OP,
        'schema', TG_TABLE_SCHEMA,
        'table', TG_TABLE_NAME,
        'data', new_row,
        'txid', txid_current(),
        'actor', actor
    )::text;

    computed_hash := encode(digest(coalesce(p_hash,'') || payload || now()::text, 'sha256'), 'hex');

    INSERT INTO public.audit_log(schema_name, table_name, operation, row_data, changed_by, txid, prev_hash, row_hash)
    VALUES (TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, new_row, actor, txid_current(), p_hash, computed_hash);

    RETURN NULL;
END;
$$ SECURITY DEFINER;

CREATE OR REPLACE VIEW public.audit_log_view AS
SELECT
  a.id,
  a.event_time,
  a.schema_name,
  a.table_name,
  a.operation,
  a.row_data,
  a.changed_by,
  u.email AS changed_by_email,
  a.txid,
  a.prev_hash,
  a.row_hash
FROM public.audit_log a
LEFT JOIN public.users u ON u.uuid_user::text = a.changed_by;

ALTER TABLE public.audit_log
    DROP COLUMN IF EXISTS event_date;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_grant_web_anon_permissions'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
