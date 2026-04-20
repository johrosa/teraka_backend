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
        """Démarre le serveur PostgREST"""
        try:
            logger.info(f"▶️  Lancement PostgREST (port {self.postgrest_port})...")
            
            # Chercher postgrest.exe ou postgrest
            postgrest_name = "postgrest.exe" if self.is_windows else "postgrest"
            postgrest_exe = DJANGO_DIR / "api" / postgrest_name
            
            # PostgREST prend le fichier de config directement en argument
            cmd = [
                str(postgrest_exe),
                str(self.postgrest_conf)
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
            
            # Pour production, utiliser gunicorn si disponible
            if self.env == "production":
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
        
        # Attendre l'arrêt
        self.wait_and_monitor()
    
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
        default=8000,
        help="Port Django (défaut: 8000)"
    )
    parser.add_argument(
        "--postgrest-port",
        type=int,
        default=3000,
        help="Port PostgREST (défaut: 3000)"
    )
    
    args = parser.parse_args()
    
    # Créer le gestionnaire et lancer
    manager = ServerManager(
        env=args.env,
        django_port=args.django_port,
        postgrest_port=args.postgrest_port
    )
    
    try:
        manager.start_all()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
