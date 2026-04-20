#!/usr/bin/env python
"""
Diagnostic des rôles et permissions RBAC dans PostgreSQL
"""
import os
import sys
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_rbac_status():
    """Vérifie l'état des rôles et permissions RBAC"""
    print("🔍 VÉRIFICATION DES RÔLES ET PERMISSIONS RBAC")
    print("=" * 70)
    
    roles_attendus = ["Expansion_L1", "Expansion_L2", "MRV_L1", "MRV_L2", "MRV_L3", "Admin_L1", "Admin_L2"]
    
    with connection.cursor() as cursor:
        # ÉTAPE 1 : Vérifier les rôles
        print("\n📋 ÉTAPE 1 : RÔLES EXISTANTS")
        print("-" * 70)
        
        for role in roles_attendus:
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [role])
            exists = cursor.fetchone()
            status = "✅ Existe" if exists else "❌ Manquant"
            print(f"  {role:<20} {status}")
        
        # ÉTAPE 2 : Vérifier les permissions sur les tables
        print("\n📋 ÉTAPE 2 : PERMISSIONS SUR LES TABLES")
        print("-" * 70)
        
        for role in roles_attendus:
            print(f"\n  Role: {role}")
            
            # Obtenir les permissions du rôle
            cursor.execute("""
                SELECT 
                    tablename,
                    CASE 
                        WHEN has_table_privilege(%s, tablename, 'SELECT') THEN 'R'
                        ELSE '-'
                    END AS read,
                    CASE 
                        WHEN has_table_privilege(%s, tablename, 'INSERT') THEN 'C'
                        ELSE '-'
                    END AS create,
                    CASE 
                        WHEN has_table_privilege(%s, tablename, 'UPDATE') THEN 'U'
                        ELSE '-'
                    END AS update,
                    CASE 
                        WHEN has_table_privilege(%s, tablename, 'DELETE') THEN 'D'
                        ELSE '-'
                    END AS delete
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """, [role, role, role, role])
            
            rows = cursor.fetchall()
            
            if rows:
                # Afficher seulement les tables avec des permissions
                tables_with_perms = [row for row in rows if any(row[i] != '-' for i in range(1, 5))]
                
                if tables_with_perms:
                    print(f"    {'Table':<40} {'Perms':<10}")
                    print(f"    {'-' * 50}")
                    for table, r, c, u, d in tables_with_perms:
                        perms = f"{c}{r}{u}{d}"
                        print(f"    {table:<40} {perms}")
                else:
                    print(f"    ⚠️  Aucune permission trouvée")
            else:
                print(f"    ⚠️  Aucune table accessible")
        
        # ÉTAPE 3 : Vérifier les permissions sur les colonnes (status_validation)
        print("\n\n📋 ÉTAPE 3 : PERMISSIONS SUR LES COLONNES (status_validation)")
        print("-" * 70)
        
        # D'abord, obtenir les tables qui ont la colonne status_validation
        cursor.execute("""
            SELECT DISTINCT table_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND column_name = 'status_validation'
            ORDER BY table_name
        """)
        
        tables_with_validation = [row[0] for row in cursor.fetchall()]
        
        if tables_with_validation:
            for role in roles_attendus:
                print(f"\n  Role: {role}")
                
                has_perms = False
                for table_name in tables_with_validation:
                    # Vérifier si le rôle a la permission UPDATE sur cette colonne
                    cursor.execute(f"""
                        SELECT has_column_privilege(%s, '{table_name}'::regclass, 'status_validation', 'UPDATE')
                    """, [role])
                    
                    has_perm = cursor.fetchone()[0]
                    if has_perm:
                        print(f"    ✅ {table_name}.status_validation")
                        has_perms = True
                
                if not has_perms:
                    print(f"    ⚠️  Aucune permission UPDATE sur status_validation")
        else:
            print(f"\n  ⚠️  Aucune table avec la colonne 'status_validation' trouvée dans le schéma 'public'")
        
        # ÉTAPE 4 : Résumé général
        print("\n\n📊 RÉSUMÉ")
        print("-" * 70)
        
        cursor.execute("""
            SELECT COUNT(DISTINCT rolname) 
            FROM pg_roles 
            WHERE rolname IN ('Expansion_L1', 'Expansion_L2', 'MRV_L1', 'MRV_L2', 'MRV_L3', 'Admin_L1', 'Admin_L2')
        """)
        role_count = cursor.fetchone()[0]
        print(f"  Rôles créés : {role_count}/7")
        
        # Vérifier authenticator
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'authenticator'")
        auth_exists = cursor.fetchone()
        print(f"  Rôle authenticator : {'✅ Existe' if auth_exists else '❌ Manquant'}")
        
        # Vérifier les membres
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_auth_members
            WHERE roleid IN (
                SELECT oid FROM pg_roles WHERE rolname IN ('Expansion_L1', 'Expansion_L2', 'MRV_L1', 'MRV_L2', 'MRV_L3', 'Admin_L1', 'Admin_L2')
            )
        """)
        member_count = cursor.fetchone()[0]
        print(f"  Memberships configurés : {member_count}")
        
        print("\n" + "=" * 70)
        print("✅ Diagnostic terminé")

if __name__ == "__main__":
    try:
        check_rbac_status()
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)