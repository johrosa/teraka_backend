#!/usr/bin/env python
"""
Script de lancement des serveurs Teraka (Django + PostgREST)
Compatible développement et production
Multiplateforme (Windows, Linux, macOS)
"""

import os
import sys
import subprocess
import signal
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Répertoire du projet
PROJECT_DIR = Path(__file__).resolve().parent
DJANGO_DIR = PROJECT_DIR

class ServerManager:
    """Gestionnaire pour les serveurs Django et PostgREST"""
    
    def __init__(self, env: str = "development", django_port: int = 8000, postgrest_port: int = 3000):
        self.env = env
        self.django_port = django_port
        self.postgrest_port = postgrest_port
        self.processes = []
        self.is_windows = sys.platform == "win32"
        
        # Fichiers de configuration
        self.postgrest_conf = DJANGO_DIR / "api" / "postgrest.conf"
        self.manage_py = DJANGO_DIR / "manage.py"
        
        logger.info(f"🔧 Environnement: {env.upper()}")
        logger.info(f"📂 Répertoire projet: {DJANGO_DIR}")
        
    def validate_environment(self) -> bool:
        """Valide que tous les fichiers nécessaires existent"""
        errors = []
        
        if not self.manage_py.exists():
            errors.append(f"manage.py introuvable à {self.manage_py}")
        
        if not self.postgrest_conf.exists():
            errors.append(f"postgrest.conf introuvable à {self.postgrest_conf}")
        
        # Chercher postgrest.exe ou postgrest selon le système
        postgrest_exe = DJANGO_DIR / "api" / ("postgrest.exe" if self.is_windows else "postgrest")
        if not postgrest_exe.exists():
            errors.append(f"PostgREST introuvable. Attendu: {postgrest_exe}")
        
        if errors:
            for error in errors:
                logger.error(f"❌ {error}")
            return False
        
        # Vérifier PostgreSQL
        self.check_postgresql()
        
        return True
    
    def check_postgresql(self):
        """Vérifie que PostgreSQL est accessible"""
        logger.info("🔍 Vérification de PostgreSQL...")
        
        try:
            import psycopg2
            conn_string = "postgres://postgres:ad,in@localhost:5432/teraka"
            # Parser le connection string
            try:
                from urllib.parse import urlparse
                parsed = urlparse(conn_string)
                host = parsed.hostname or 'localhost'
                port = parsed.port or 5432
                user = parsed.username or 'postgres'
                password = parsed.password or ''
                db = parsed.path.lstrip('/') or 'teraka'
                
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=db,
                    connect_timeout=5
                )
                conn.close()
                logger.info("✓ PostgreSQL accessible")
                return True
            except Exception as db_err:
                logger.warning(f"⚠️  PostgreSQL non accessible: {db_err}")
                logger.warning("   Assurez-vous que PostgreSQL est en cours d'exécution")
                logger.warning("   Et que la base de données 'teraka' existe")
                return False
        except ImportError:
            logger.warning("⚠️  psycopg2 non installé - impossible de vérifier PostgreSQL")
            logger.warning("   Installez-le: pip install psycopg2-binary")
            return False
    
    def setup_environment(self):
        """Configure les variables d'environnement selon l'environnement"""
        if self.env == "production":
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
            os.environ["ENV"] = "production"
            logger.info("⚙️  Configuration PRODUCTION activée")
        else:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
            os.environ["ENV"] = "development"
            logger.info("⚙️  Configuration DÉVELOPPEMENT activée")
    
    def start_postgrest(self) -> Optional[subprocess.Popen]:
        """Démarre le serveur PostgREST en générant un fichier de config temporaire
        qui fixe server-port et db-uri à la valeur souhaitée (self.postgrest_port et DB settings).
        """
        try:
            logger.info(f"▶️  Lancement PostgREST (port {self.postgrest_port})...")
            
            # Chercher postgrest.exe ou postgrest
            postgrest_name = "postgrest.exe" if self.is_windows else "postgrest"
            postgrest_exe = DJANGO_DIR / "api" / postgrest_name
            
            # Récupérer les informations de DB depuis Django settings ou variables d'environnement
            try:
                from django.conf import settings as dj_settings
            except Exception:
                dj_settings = None

            def build_db_uri():
                # Build DB URI strictly from Django settings when available.
                try:
                    from urllib.parse import quote_plus
                    if not dj_settings:
                        raise RuntimeError('Django settings not available')
                    # Prefer explicit DATABASE_URL in settings if provided
                    db_url = getattr(dj_settings, 'DATABASE_URL', None)
                    if db_url:
                        return db_url
                    user = getattr(dj_settings, 'DB_USER', 'postgres')
                    password = getattr(dj_settings, 'DB_PASSWORD', '')
                    host = getattr(dj_settings, 'DB_HOST', 'localhost')
                    port = getattr(dj_settings, 'DB_PORT', '5432')
                    name = getattr(dj_settings, 'DB_NAME', 'teraka')
                    # URL-encode user/password
                    user_enc = quote_plus(str(user)) if user is not None else ''
                    password_enc = quote_plus(str(password)) if password is not None else ''
                    return f"postgres://{user_enc}:{password_enc}@{host}:{port}/{name}"
                except Exception:
                    logger.error("Django settings unavailable — falling back to hardcoded DB URI")
                    return "postgres://postgres:@localhost:5432/teraka"

            db_uri = build_db_uri()

            # Générer un fichier de config temporaire avec le bon server-port et db-uri
            try:
                template_path = DJANGO_DIR / "api" / "postgrest.conf.j2"
                if template_path.exists():
                    logger.info(f"📝 Utilisation du template PostgREST: {template_path}")
                    template_text = template_path.read_text(encoding='utf-8')
                    context = {
                        'db_uri': db_uri,
                        'db_schema': getattr(dj_settings, 'DB_SCHEMA', 'public') if dj_settings else 'public',
                        'db_anon_role': getattr(dj_settings, 'DB_ANON_ROLE', 'web_anon') if dj_settings else 'web_anon',
                        'jwt_secret': getattr(dj_settings, 'SIMPLE_JWT', {}).get('SIGNING_KEY', getattr(dj_settings, 'SECRET_KEY', '')) if dj_settings else '',
                        'server_host': getattr(dj_settings, 'POSTGREST_HOST', '0.0.0.0') if dj_settings else '0.0.0.0',
                        'server_port': self.postgrest_port,
                        'max_rows': getattr(dj_settings, 'POSTGREST_MAX_ROWS', 1000) if dj_settings else 1000,
                    }
                    logger.debug(f"   Context pour template: {context}")
                    # Prefer jinja2 if available for full templating support
                    try:
                        import jinja2
                        rendered = jinja2.Template(template_text).render(**context)
                        logger.info("   ✓ Template rendu avec Jinja2")
                    except ImportError:
                        logger.info("   ℹ️  Jinja2 non disponible, utilisation du simple replace")
                        # Simple fallback: replace common {{ key }} placeholders
                        rendered = template_text
                        for k, v in context.items():
                            rendered = rendered.replace(f"{{{{ {k} }}}}", str(v))
                            rendered = rendered.replace(f"{{{{{k}}}}}", str(v))
                    except Exception as jinja_err:
                        logger.warning(f"   ⚠️  Erreur Jinja2: {jinja_err}, utilisation du simple replace")
                        rendered = template_text
                        for k, v in context.items():
                            rendered = rendered.replace(f"{{{{ {k} }}}}", str(v))
                            rendered = rendered.replace(f"{{{{{k}}}}}", str(v))
                    temp_conf_path = DJANGO_DIR / "api" / f"postgrest.generated.{self.postgrest_port}.conf"
                    temp_conf_path.write_text(rendered, encoding='utf-8')
                    logger.info(f"   📄 Config PostgREST générée: {temp_conf_path}")
                    logger.debug(f"   Contenu de la config:")
                    for line in rendered.splitlines():
                        if 'secret' in line.lower() or 'password' in line.lower():
                            logger.debug(f"      {line[:30]}***[MASKED]***")
                        else:
                            logger.debug(f"      {line}")
                else:
                    logger.warning(f"⚠️  Template {template_path} non trouvé, utilisation du fallback (modification de config)")
                    # Fallback to previous behavior of modifying existing conf if no template exists
                    original_conf = self.postgrest_conf.read_text(encoding='utf-8')
                    new_conf_lines = []
                    replaced_port = False
                    replaced_dburi = False
                    for line in original_conf.splitlines():
                        stripped = line.strip()
                        if stripped.startswith('server-port'):
                            new_conf_lines.append(f'server-port = {self.postgrest_port}')
                            replaced_port = True
                        elif stripped.startswith('db-uri'):
                            new_conf_lines.append(f'db-uri = "{db_uri}"')
                            replaced_dburi = True
                        else:
                            new_conf_lines.append(line)
                    if not replaced_port:
                        new_conf_lines.append(f'server-port = {self.postgrest_port}')
                    if not replaced_dburi:
                        insert_at = 0
                        for idx, l in enumerate(new_conf_lines):
                            if l.strip().startswith('#'):
                                continue
                            insert_at = idx
                            break
                        new_conf_lines.insert(insert_at, f'db-uri = "{db_uri}"')
                    temp_conf_path = DJANGO_DIR / "api" / f"postgrest.generated.{self.postgrest_port}.conf"
                    temp_conf_path.write_text('\n'.join(new_conf_lines), encoding='utf-8')
                    logger.info(f"   📄 Config PostgREST générée (fallback): {temp_conf_path}")
            except Exception as e:
                logger.warning(f"⚠️  Impossible de générer le fichier de conf PostgREST: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                temp_conf_path = self.postgrest_conf
            
            # PostgREST prend le fichier de config directement en argument
            cmd = [
                str(postgrest_exe),
                str(temp_conf_path)
            ]
            
            # Afficher la commande en debug
            logger.debug(f"   Commande: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                cwd=str(DJANGO_DIR / "api"),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid if not self.is_windows else None
            )
            
            logger.info(f"✓ PostgREST démarré (PID: {process.pid})")
            
            # Thread pour lire les logs
            import threading
            log_thread = threading.Thread(
                target=self._read_process_logs,
                args=(process, "PostgREST"),
                daemon=True
            )
            log_thread.start()
            
            return process
            
        except FileNotFoundError as e:
            logger.error(f"❌ PostgREST exécutable non trouvé: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur au lancement de PostgREST: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _read_process_logs(self, process, name):
        """Lit les logs d'un processus dans un thread séparé"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.rstrip('\n')
                    # Filtrer les logs verbeux
                    if line.strip():
                        logger.info(f"[{name}] {line}")
        except Exception as e:
            logger.debug(f"Erreur lors de la lecture des logs {name}: {e}")
    
    def start_django(self) -> Optional[subprocess.Popen]:
        """Démarre le serveur Django"""
        try:
            logger.info(f"▶️  Lancement Django (port {self.django_port})...")
            
            # Pour production, utiliser gunicorn sur Unix. Sur Windows, Gunicorn ne fonctionne pas
            # correctement car il dépend de fcntl. En local sur Windows, on utilise le serveur Django.
            if self.env == "production" and not self.is_windows:
                cmd = [
                    sys.executable,
                    "-m", "gunicorn",
                    "config.wsgi:application",
                    f"--bind=0.0.0.0:{self.django_port}",
                    "--workers=4",
                    "--timeout=120",
                    "--access-logfile=-",
                    "--error-logfile=-"
                ]
                logger.info("   (Mode: Gunicorn)")
            else:
                cmd = [
                    sys.executable,
                    str(self.manage_py),
                    "runserver",
                    f"0.0.0.0:{self.django_port}"
                ]
                if self.env == "production":
                    logger.info("   (Mode: Django development server fallback sur Windows)")
                else:
                    logger.info("   (Mode: Django development server)")
            
            # Afficher la commande en debug
            logger.debug(f"   Commande: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                cwd=str(DJANGO_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid if not self.is_windows else None
            )
            
            logger.info(f"✓ Django démarré (PID: {process.pid})")
            
            # Thread pour lire les logs
            import threading
            log_thread = threading.Thread(
                target=self._read_process_logs,
                args=(process, "Django"),
                daemon=True
            )
            log_thread.start()
            
            return process
            
        except Exception as e:
            logger.error(f"❌ Erreur au lancement de Django: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def start_all(self):
        """Démarre tous les serveurs"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("🚀 DÉMARRAGE DES SERVEURS TERAKA")
        logger.info("=" * 60)
        logger.info("")
        
        # Validation
        if not self.validate_environment():
            logger.error("❌ Validation de l'environnement échouée")
            logger.info("")
            logger.info("📋 Dépannage:")
            logger.info("   1. Assurez-vous que PostgreSQL est en cours d'exécution")
            logger.info("   2. Vérifiez la base de données 'teraka' existe")
            logger.info("   3. Vérifiez les credentials dans api/postgrest.conf")
            logger.info("   4. Vérifiez les logs ci-dessus pour plus de détails")
            sys.exit(1)
        
        # Setup
        self.setup_environment()
        
        # Attendre un peu avant de démarrer
        time.sleep(1)
        
        # Lancer les serveurs
        logger.info("")
        postgrest_proc = self.start_postgrest()
        if postgrest_proc:
            self.processes.append(postgrest_proc)
        else:
            logger.error("❌ Impossible de démarrer PostgREST")
            sys.exit(1)
        
        # Attendre que PostgREST soit prêt
        time.sleep(2)
        
        django_proc = self.start_django()
        if django_proc:
            self.processes.append(django_proc)
        else:
            logger.error("❌ Impossible de démarrer Django")
            # Arrêter PostgREST
            if postgrest_proc:
                postgrest_proc.terminate()
            sys.exit(1)
        
        if not self.processes:
            logger.error("❌ Aucun serveur n'a pu être démarré")
            sys.exit(1)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ Serveurs en cours d'exécution")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📍 Accès:")
        logger.info(f"   • Django Admin : http://localhost:{self.django_port}/admin/")
        logger.info(f"   • Login API    : http://localhost:{self.django_port}/api/login/")
        logger.info(f"   • PostgREST    : http://localhost:{self.postgrest_port}")
        logger.info("")
        logger.info("🛑 Pressez Ctrl+C pour arrêter les serveurs")
        logger.info("=" * 60)
        logger.info("")
        
        # Test les serveurs après un délai de stabilisation plus long
        time.sleep(5)
        self.run_health_checks()
        
        # Attendre l'arrêt
        self.wait_and_monitor()
    
    def run_health_checks(self):
        """Teste les endpoints clés après le démarrage"""
        from urllib.request import Request, urlopen
        from urllib.error import URLError, HTTPError
        import json as json_lib
        
        logger.info("")
        logger.info("🧪 Tests de santé des API (peut prendre quelques secondes)...")
        logger.info("")
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Django health
        tests_total += 1
        try:
            req = Request(f"http://0.0.0.0:{self.django_port}/", method='GET')
            with urlopen(req, timeout=3) as resp:
                logger.info(f"   ✓ Django: {resp.status}")
                tests_passed += 1
        except Exception as e:
            logger.debug(f"   ⚠️  Django: {type(e).__name__}: {e}")
        
        # Test 2: PostgREST direct
        tests_total += 1
        try:
            req = Request(f"http://0.0.0.0:{self.postgrest_port}/communes?limit=1", method='GET')
            with urlopen(req, timeout=3) as resp:
                data = json_lib.loads(resp.read().decode())
                logger.info(f"   ✓ PostgREST direct: {len(data)} records")
                tests_passed += 1
        except Exception as e:
            logger.debug(f"   ⚠️  PostgREST direct: {type(e).__name__}: {e}")
        
        # Test 3: PostgREST info endpoint
        tests_total += 1
        try:
            req = Request(f"http://0.0.0.0:{self.django_port}/api/postgrest-info/", method='GET')
            with urlopen(req, timeout=3) as resp:
                data = json_lib.loads(resp.read().decode())
                logger.info(f"   ✓ PostgREST info: {data.get('postgrest_upstream')}")
                tests_passed += 1
        except Exception as e:
            logger.debug(f"   ⚠️  PostgREST info: {type(e).__name__}: {e}")
        
        # Test 4: PostgREST proxy
        tests_total += 1
        try:
            req = Request(f"http://0.0.0.0:{self.django_port}/api/data/communes?limit=1", method='GET')
            with urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json_lib.loads(resp.read().decode())
                    logger.info(f"   ✓ PostgREST proxy: {len(data)} records")
                    tests_passed += 1
                else:
                    logger.debug(f"   ⚠️  PostgREST proxy: HTTP {resp.status}")
        except HTTPError as e:
            if e.code == 401:
                logger.info(f"   ℹ️  PostgREST proxy: {e.code} (auth required - expected)")
                tests_passed += 1
            else:
                logger.debug(f"   ⚠️  PostgREST proxy: HTTP {e.code}: {e}")
        except Exception as e:
            logger.debug(f"   ⚠️  PostgREST proxy: {type(e).__name__}: {e}")
        
        logger.info("")
        logger.info(f"📊 Résumé: {tests_passed}/{tests_total} tests réussis")
        if tests_passed == tests_total:
            logger.info("✓ Tous les tests sont passés!")
        elif tests_passed >= tests_total - 1:
            logger.info("⚠️  La plupart des tests sont passés, vérifiez les logs si nécessaire")
        else:
            logger.warning("❌ Plusieurs tests ont échoué")
            logger.info("   (Les serveurs démarrent peut-être encore, attendez quelques secondes)")
        logger.info("")
    
    def wait_and_monitor(self):
        """Attends que les processus se terminent et les monitore"""
        try:
            first_check = True
            while True:
                # Vérifier que les processus tournent toujours
                for i, proc in enumerate(self.processes, 1):
                    if proc.poll() is not None:
                        # Le processus s'est arrêté
                        if first_check:
                            # C'est probablement une erreur au démarrage
                            stderr = proc.stderr.read() if proc.stderr else ""
                            stdout = proc.stdout.read() if proc.stdout else ""
                            logger.error(f"")
                            logger.error(f"❌ ERREUR: Serveur {i} n'a pas pu démarrer")
                            if stdout:
                                logger.error(f"   Output: {stdout}")
                            if stderr:
                                logger.error(f"   Erreur: {stderr}")
                        else:
                            logger.warning(f"⚠️  Processus {i} s'est arrêté de manière inattendue (exit code: {proc.returncode})")
                
                first_check = False
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Arrêt des serveurs...")
            self.stop_all()
    
    def stop_all(self):
        """Arrête tous les serveurs proprement"""
        for i, proc in enumerate(self.processes, 1):
            try:
                if self.is_windows:
                    # Sur Windows, utiliser SIGTERM
                    proc.terminate()
                else:
                    # Sur Unix, tuer le groupe de processus
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                
                # Attendre l'arrêt gracieux
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Forcer l'arrêt après 5 secondes
                    if self.is_windows:
                        proc.kill()
                    else:
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                
                logger.info(f"✓ Serveur {i} arrêté")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'arrêt du serveur {i}: {e}")
        
        logger.info("✓ Tous les serveurs sont arrêtés")


def main():
    """Fonction principale"""
    import argparse
    
    # Permet d'importer les settings pour récupérer les ports par défaut si nécessaire
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.conf import settings as dj_settings
    except Exception:
        dj_settings = None

    parser = argparse.ArgumentParser(
        description="Lance les serveurs Teraka (Django + PostgREST)"
    )
    parser.add_argument(
        "--env",
        choices=["development", "production"],
        default="development",
        help="Environnement d'exécution (défaut: development)"
    )
    parser.add_argument(
        "--django-port",
        type=int,
        default=None,
        help="Port Django (défaut: settings.DJANGO_PORT or 8000)"
    )
    parser.add_argument(
        "--postgrest-port",
        type=int,
        default=None,
        help="Port PostgREST (défaut: settings.POSTGREST_PORT or 3000)"
    )
    
    args = parser.parse_args()

    # Déterminer les ports en priorité: CLI args > Django settings > ENV > hardcoded defaults    
    if dj_settings:
        default_django_port = getattr(dj_settings, 'DJANGO_PORT', 8000)
        default_postgrest_port = getattr(dj_settings, 'POSTGREST_PORT', 3000)
    else:
        default_django_port = int(os.environ.get('DJANGO_PORT', 8000))
        default_postgrest_port = int(os.environ.get('POSTGREST_PORT', 3000))

    django_port = args.django_port if args.django_port is not None else default_django_port
    postgrest_port = args.postgrest_port if args.postgrest_port is not None else default_postgrest_port

    # Créer le gestionnaire et lancer
    manager = ServerManager(
        env=args.env,
        django_port=django_port,
        postgrest_port=postgrest_port
    )
    
    try:
        manager.start_all()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
