from django.core.management.base import BaseCommand
from django.db import connection, transaction
import time


class Command(BaseCommand):
    help = 'Run quick test of audit_log: create test table, fire DML, show audit rows and verify hash chain.'

    def handle(self, *args, **options):
        with connection.cursor() as cur:
            self.stdout.write('Creating test table...')
            cur.execute("CREATE TABLE IF NOT EXISTS public.test_audit_table (id serial PRIMARY KEY, data text)")

            self.stdout.write('(Re)creating trigger for test table...')
            cur.execute("DROP TRIGGER IF EXISTS audit_test_audit_table ON public.test_audit_table")
            cur.execute("CREATE TRIGGER audit_test_audit_table AFTER INSERT OR UPDATE OR DELETE ON public.test_audit_table FOR EACH ROW EXECUTE FUNCTION public.audit_log_trigger();")

            self.stdout.write('Cleaning existing test data...')
            cur.execute("DELETE FROM public.test_audit_table")
            cur.execute("DELETE FROM public.audit_log WHERE table_name='test_audit_table'")

            self.stdout.write('Performing INSERT, UPDATE, DELETE...')
            cur.execute("INSERT INTO public.test_audit_table(data) VALUES ('first') RETURNING id")
            row = cur.fetchone()
            cur.execute("UPDATE public.test_audit_table SET data='first-updated' WHERE id=%s", [row[0]])
            cur.execute("DELETE FROM public.test_audit_table WHERE id=%s", [row[0]])

            # small sleep to ensure timestamps are stable
            time.sleep(0.1)

            self.stdout.write('\nAudit log entries for test_audit_table:')
            cur.execute("SELECT id, event_time, operation, changed_by, txid, prev_hash, row_hash, row_data FROM public.audit_log WHERE table_name='test_audit_table' ORDER BY id")
            rows = cur.fetchall()

            if not rows:
                self.stdout.write('No audit rows found. Did you run migrations?')
                return

            for r in rows:
                self.stdout.write(f'id={r[0]} time={r[1]} op={r[2]} by={r[3]} txid={r[4]} prev_hash={r[5]} row_hash={r[6]} data={r[7]}')

            self.stdout.write('\nVerifying hash chain (recomputing):')
            # Recompute using same logic as trigger but based on stored values (uses event_time text)
            cur.execute("""
                SELECT id, prev_hash, row_hash,
                   encode(digest(coalesce(prev_hash,'') || (jsonb_build_object('op', operation, 'schema', schema_name, 'table', table_name, 'data', row_data, 'txid', txid, 'actor', changed_by)::text) || event_time::text, 'sha256'), 'hex') AS recomputed
                FROM public.audit_log
                WHERE table_name='test_audit_table'
                ORDER BY id
            """)
            ver = cur.fetchall()
            ok = True
            for v in ver:
                self.stdout.write(f'id={v[0]} prev={v[1]} stored_hash={v[2]} recomputed={v[3]} match={v[2]==v[3]}')
                if v[2] != v[3]:
                    ok = False

            if ok:
                self.stdout.write('\nHash chain OK')
            else:
                self.stdout.write('\nHash chain MISMATCH detected')

            self.stdout.write('\nSimulating tamper: corrupt first audit row\n')
            cur.execute("SELECT id FROM public.audit_log WHERE table_name='test_audit_table' ORDER BY id LIMIT 1")
            first = cur.fetchone()
            if first:
                cur.execute("UPDATE public.audit_log SET row_hash = 'deadbeef' WHERE id=%s", [first[0]])
                cur.execute("SELECT id, row_hash, encode(digest(coalesce(prev_hash,'') || (jsonb_build_object('op', operation, 'schema', schema_name, 'table', table_name, 'data', row_data, 'txid', txid, 'actor', changed_by)::text) || event_time::text, 'sha256'), 'hex') AS recomputed FROM public.audit_log WHERE table_name='test_audit_table' ORDER BY id")
                tam = cur.fetchall()
                for t in tam:
                    self.stdout.write(f'id={t[0]} stored_hash={t[1]} recomputed={t[2]} match={t[1]==t[2]}')
                self.stdout.write('\nTamper simulation complete — chain should show mismatch')
            else:
                self.stdout.write('No audit rows to tamper with')
