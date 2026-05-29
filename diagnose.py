#!/usr/bin/env python
"""
Script de diagnostic pour Teraka Platform
Vérifie que tous les prérequis sont satisfaits
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

def print_section(title):
    """Affiche une section de titre"""
    print("")
    print("=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def check_python():
    """Vérifie la version de Python"""
    print(f"✓ Python {sys.version}")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ requis, vous avez {sys.version_info.major}.{sys.version_info.minor}")
        return False
    return True

def check_files():
    """Vérifie que les fichiers nécessaires existent"""
    files_to_check = [
        ("manage.py", PROJECT_DIR / "manage.py"),
        ("api/postgrest.conf", PROJECT_DIR / "api" / "postgrest.conf"),
        ("api/postgrest.exe" if sys.platform == "win32" else "api/postgrest", 
         PROJECT_DIR / "api" / ("postgrest.exe" if sys.platform == "win32" else "postgrest")),
    ]
    
    all_ok = True
    for name, path in files_to_check:
        if path.exists():
            print(f"✓ {name}")
        else:
            print(f"❌ {name} - Introuvable à {path}")
            all_ok = False
    
    return all_ok

def check_python_packages():
    """Vérifie que les packages Python essentiels sont installés"""
    packages = {
        "django": "django",
        "djangorestframework": "rest_framework",
        "rest_framework_simplejwt": "rest_framework_simplejwt",
        "pandas": "pandas",
        "psycopg2": "psycopg2",
        "django-cors-headers": "corsheaders",
        "django-jazzmin": "jazzmin",
    }
    
    missing = []
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NON installé")
            missing.append(package_name)
    
    if missing:
        print(f"\n📦 Pour installer les packages manquants:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_postgresql():
    """Vérifie que PostgreSQL est accessible"""
    try:
        import psycopg2
        
        # Lire la config PostgREST
        conf_file = PROJECT_DIR / "api" / "postgrest.conf"
        db_uri = None
        
        if conf_file.exists():
            with open(conf_file) as f:
                for line in f:
                    if line.startswith('db-uri'):
                        # Extraire le URI
                        db_uri = line.split('=')[1].strip().strip('"')
                        break
        
        if not db_uri:
            print("❌ Impossible de trouver db-uri dans postgrest.conf")
            return False
        
        # Parser le connection string
        from urllib.parse import urlparse
        parsed = urlparse(db_uri)
        
        host = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        user = parsed.username or 'postgres'
        password = parsed.password or ''
        db = parsed.path.lstrip('/') or 'postgres'
        
        print(f"   Connexion à: {user}@{host}:{port}/{db}")
        
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db,
                connect_timeout=5
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            print(f"✓ PostgreSQL accessible")
            print(f"   Version: {version.split(',')[0]}")
            return True
            
        except psycopg2.OperationalError as e:
            print(f"❌ Impossible de se connecter à PostgreSQL")
            print(f"   Erreur: {e}")
            print(f"\n   💡 Solutions:")
            print(f"      • Vérifier que PostgreSQL est en cours d'exécution")
            print(f"      • Vérifier les credentials dans api/postgrest.conf")
            print(f"      • Vérifier que la base de données '{db}' existe")
            print(f"      • Vérifier le firewall")
            return False
            
    except ImportError:
        print("⚠️  psycopg2 non installé")
        print(f"   Impossible de vérifier PostgreSQL")
        print(f"   Installez: pip install psycopg2-binary")
        return False

def check_ports():
    """Vérifie que les ports ne sont pas utilisés"""
    ports = {"Django": 8000, "PostgREST": 3000}
    
    all_ok = True
    for name, port in ports.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"⚠️  {name} (:{port}) - Port UTILISÉ")
                print(f"   Quelque chose tourne déjà sur ce port")
                all_ok = False
            else:
                print(f"✓ {name} (:{port}) - Port disponible")
        except Exception as e:
            print(f"⚠️  Impossible de vérifier le port {name} ({port}): {e}")
    
    return all_ok

def check_postgis():
    """Vérifie que PostGIS est installé dans PostgreSQL"""
    try:
        import psycopg2
        
        conf_file = PROJECT_DIR / "api" / "postgrest.conf"
        db_uri = None
        
        if conf_file.exists():
            with open(conf_file) as f:
                for line in f:
                    if line.startswith('db-uri'):
                        db_uri = line.split('=')[1].strip().strip('"')
                        break
        
        if not db_uri:
            return None
        
        from urllib.parse import urlparse
        parsed = urlparse(db_uri)
        
        host = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        user = parsed.username or 'postgres'
        password = parsed.password or ''
        db = parsed.path.lstrip('/') or 'postgres'
        
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db,
                connect_timeout=5
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'postgis';")
            has_postgis = cursor.fetchone() is not None
            cursor.close()
            conn.close()
            
            if has_postgis:
                print(f"✓ PostGIS installé")
                return True
            else:
                print(f"⚠️  PostGIS non trouvé dans la base de données")
                print(f"   Vous en aurez besoin pour les données géospatiales")
                return True  # Pas critique
            
        except Exception as e:
            print(f"⚠️  Impossible de vérifier PostGIS: {e}")
            return None
            
    except ImportError:
        print("⚠️  psycopg2 non installé - impossible de vérifier PostGIS")
        return None

def check_django_csrf():
    """Vérifie que Django peut démarrer sans erreurs CSRF"""
    try:
        import os
        import django
        from django.conf import settings
        
        # Configurer Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        # Tester l'import des vues
        from core.views import LoginForPostgrestView, PostgrestProxyView
        from core.admin import RBACAdmin
        
        # Tester que les templates existent
        from django.template.loader import get_template
        try:
            get_template('admin/csv_form.html')
            get_template('admin/rbac_change_list.html')
            print("✓ Templates admin accessibles")
        except Exception as e:
            print(f"⚠️  Problème avec les templates: {e}")
            return False
        
        print("✓ Configuration Django CSRF OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Django/CSRF: {e}")
        return False

def main():
    """Fonction principale"""
    print("")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🔧 DIAGNOSTIC - TERAKA PLATFORM BACKEND".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    checks = [
        ("Python", check_python),
        ("Fichiers", check_files),
        ("Packages Python", check_python_packages),
        ("Ports disponibles", check_ports),
        ("PostgreSQL", check_postgresql),
        ("PostGIS", check_postgis),
        ("Django/CSRF", check_django_csrf),
    ]
    
    results = {}
    for title, check_func in checks:
        print_section(title)
        try:
            result = check_func()
            results[title] = result
        except Exception as e:
            print(f"❌ Erreur lors du diagnostic: {e}")
            import traceback
            traceback.print_exc()
            results[title] = False
    
    # Résumé
    print_section("📊 RÉSUMÉ")
    
    ok_count = sum(1 for v in results.values() if v is True)
    total_count = len([v for v in results.values() if v is not None])
    
    for title, result in results.items():
        if result is True:
            print(f"✓ {title}")
        elif result is False:
            print(f"❌ {title}")
        elif result is None:
            print(f"⚠️  {title}")
    
    print("")
    print(f"Résultat: {ok_count}/{total_count} vérifications réussies")
    
    if ok_count == total_count:
        print("")
        print("✅ Tous les prérequis sont satisfaits!")
        print("   Vous pouvez maintenant lancer les serveurs:")
        print(f"   python run_servers.py")
        return 0
    else:
        print("")
        print("⚠️  Certains problèmes ont été détectés.")
        print("   Veuillez les corriger avant de lancer les serveurs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
