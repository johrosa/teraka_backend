"""Create tamper-evident audit_log table, trigger function and triggers for all public tables.

This migration:
- enables pgcrypto (digest)
- creates public.audit_log
- creates public.audit_log_trigger() SECURITY DEFINER
- attaches the trigger to every public table except audit_log and django_* tables

The trigger records operation, full row as jsonb, txid and computes a SHA256 hash
that chains to the previous row_hash for the same table (tamper-evident per-table chain).
"""
from django.db import migrations

sql = r"""
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS public.audit_log (
    id bigserial PRIMARY KEY,
    event_time timestamptz NOT NULL DEFAULT now(),
    schema_name text NOT NULL,
    table_name text NOT NULL,
    operation text NOT NULL,
    row_data jsonb,
    changed_by text,
    txid bigint DEFAULT txid_current(),
    prev_hash text,
    row_hash text
);

REVOKE INSERT, UPDATE, DELETE ON public.audit_log FROM PUBLIC;
COMMENT ON TABLE public.audit_log IS 'Tamper-evident audit log: rows chained by SHA256';

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

-- Attach triggers to all public tables except audit_log and django_migrations tables
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT table_schema, table_name FROM information_schema.tables
    WHERE table_schema='public' AND table_type='BASE TABLE' AND table_name NOT IN ('audit_log') AND table_name NOT LIKE 'django_%'
  LOOP
    BEGIN
      EXECUTE format('CREATE TRIGGER %I AFTER INSERT OR UPDATE OR DELETE ON %I.%I FOR EACH ROW EXECUTE FUNCTION public.audit_log_trigger();', 'audit_' || r.table_name, r.table_schema, r.table_name);
    EXCEPTION WHEN duplicate_object THEN
      -- already exists, ignore
      NULL;
    END;
  END LOOP;
END;
$$;
"""

reverse_sql = r"""
-- Drop the created triggers
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT table_schema, table_name FROM information_schema.tables
    WHERE table_schema='public' AND table_type='BASE TABLE' AND table_name NOT IN ('audit_log') AND table_name NOT LIKE 'django_%'
  LOOP
    BEGIN
      EXECUTE format('DROP TRIGGER IF EXISTS %I ON %I.%I;', 'audit_' || r.table_name, r.table_schema, r.table_name);
    EXCEPTION WHEN others THEN
      NULL;
    END;
  END LOOP;
END;
$$;

DROP FUNCTION IF EXISTS public.audit_log_trigger();
DROP TABLE IF EXISTS public.audit_log;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_users_role_enum_rbac_roles'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
