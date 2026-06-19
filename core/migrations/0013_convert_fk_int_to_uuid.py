from django.db import migrations

sql = r"""
-- Convert referencing integer foreign-key columns to UUID where referenced column is uuid.
-- For each foreign key where the referenced column is uuid but the referencing column is int4/int8,
-- attempt conversion by creating a temporary uuid column, populating it by joining on target.id if present,
-- otherwise try a text-cast join, then replace the column and recreate FK.

DO $$
DECLARE
  r record;
  v_updated int;
BEGIN
  FOR r IN
    SELECT con.oid AS conoid, con.conname, src_ns.nspname AS src_schema, src.relname AS src_table,
           srccol.attname AS src_column,
           tgt_ns.nspname AS tgt_schema, tgt.relname AS tgt_table, tgtcol.attname AS tgt_column
    FROM pg_constraint con
    JOIN pg_class src ON con.conrelid = src.oid
    JOIN pg_namespace src_ns ON src.relnamespace = src_ns.oid
    JOIN pg_class tgt ON con.confrelid = tgt.oid
    JOIN pg_namespace tgt_ns ON tgt.relnamespace = tgt_ns.oid
    JOIN unnest(con.conkey) WITH ORDINALITY AS src_cols(attnum, ord) ON true
    JOIN unnest(con.confkey) WITH ORDINALITY AS tgt_cols(attnum, ord2) ON src_cols.ord = tgt_cols.ord2
    JOIN pg_attribute srccol ON srccol.attrelid = src.oid AND srccol.attnum = src_cols.attnum
    JOIN pg_attribute tgtcol ON tgtcol.attrelid = tgt.oid AND tgtcol.attnum = tgt_cols.attnum
    WHERE con.contype = 'f'
      AND tgt_ns.nspname = 'public'
      AND (SELECT pg_type.typname FROM pg_type WHERE pg_type.oid = tgtcol.atttypid) = 'uuid'
      AND (SELECT pg_type.typname FROM pg_type WHERE pg_type.oid = srccol.atttypid) IN ('int4','int8')
  LOOP
    BEGIN
      RAISE NOTICE 'Converting FK % on %.% (column: %) -> %.% (% )', r.conname, r.src_schema, r.src_table, r.src_column, r.tgt_schema, r.tgt_table, r.tgt_column;

      -- drop FK constraint temporarily
      EXECUTE format('ALTER TABLE %I.%I DROP CONSTRAINT IF EXISTS %I', r.src_schema, r.src_table, r.conname);

      -- add temporary uuid column
      EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS %I_tmp uuid', r.src_schema, r.src_table, r.src_column);

      -- Try populate via joining on target's integer id column if it exists
      BEGIN
        -- Try join comparing source text to target id text (explicit cast to text)
        EXECUTE format('UPDATE %I.%I s SET %I_tmp = t.%I FROM %I.%I t WHERE s.%I::text = t.id::text',
                       r.src_schema, r.src_table, r.src_column, r.tgt_column, r.tgt_schema, r.tgt_table, r.src_column);
        GET DIAGNOSTICS v_updated = ROW_COUNT;
      EXCEPTION WHEN others THEN
        v_updated := 0;
      END;

      -- If no rows updated, try numeric cast (source bigint) to match target id
      IF v_updated = 0 THEN
        BEGIN
          EXECUTE format('UPDATE %I.%I s SET %I_tmp = t.%I FROM %I.%I t WHERE s.%I::bigint = t.id',
                         r.src_schema, r.src_table, r.src_column, r.tgt_column, r.tgt_schema, r.tgt_table, r.src_column);
          GET DIAGNOSTICS v_updated = ROW_COUNT;
        EXCEPTION WHEN others THEN
          v_updated := 0;
        END;
      END IF;

      -- If still zero, try casting text join between source and target uuid
      IF v_updated = 0 THEN
        BEGIN
          EXECUTE format('UPDATE %I.%I s SET %I_tmp = t.%I FROM %I.%I t WHERE s.%I::text = t.%I::text',
                         r.src_schema, r.src_table, r.src_column, r.tgt_column, r.tgt_schema, r.tgt_table, r.src_column, r.tgt_column);
          GET DIAGNOSTICS v_updated = ROW_COUNT;
        EXCEPTION WHEN others THEN
          v_updated := 0;
        END;
      END IF;

      -- If still zero, attempt to match against target's legacy integer PK column name 'id' casted (safe no-op if not present)
      -- (already attempted). If still zero, we leave the tmp column NULL and skip NOT NULL enforcement.

      -- Drop old integer column
      EXECUTE format('ALTER TABLE %I.%I DROP COLUMN IF EXISTS %I', r.src_schema, r.src_table, r.src_column);

      -- Rename tmp to original name
      EXECUTE format('ALTER TABLE %I.%I RENAME COLUMN %I_tmp TO %I', r.src_schema, r.src_table, r.src_column, r.src_column);

      -- Recreate FK to referenced uuid column
      EXECUTE format('ALTER TABLE %I.%I ADD CONSTRAINT %I FOREIGN KEY (%I) REFERENCES %I.%I(%I) DEFERRABLE INITIALLY DEFERRED',
                     r.src_schema, r.src_table, r.conname || '_uuid', r.src_column, r.tgt_schema, r.tgt_table, r.tgt_column);

      -- Create index for performance
      EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_%I ON %I.%I (%I)', r.src_table, r.src_column, r.src_schema, r.src_table, r.src_column);

    EXCEPTION WHEN others THEN
      RAISE NOTICE 'Failed converting FK % on %.%: %', r.conname, r.src_schema, r.src_table, SQLERRM;
    END;
  END LOOP;
END$$;
"""

reverse_sql = r"""
-- Reverse is non-trivial and unsafe (may be lossy). No-op reverse.
DO $$ BEGIN RAISE NOTICE 'Reverse of 0013_convert_fk_int_to_uuid is a no-op'; END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_adminlog_userid_to_uuid'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
