from django.contrib.gis import admin
from django.apps import apps

app_models = apps.get_app_config('core').get_models()

for model in app_models:
    try:
        # On crée une classe qui hérite de GISModelAdmin
        @admin.register(model)
        class DynamicGeoAdmin(admin.GISModelAdmin):
            list_display = [field.name for field in model._meta.fields]

            # Paramètres pour forcer l'affichage de la carte
            gis_widget_kwargs = {
                'attrs': {
                    'default_zoom': 11,
                    'scrollable': True,
                    'map_width': 700,
                    'map_height': 400,
                }
            }
    except admin.sites.AlreadyRegistered:
        pass

import pandas as pd
from django import forms
from django.contrib import admin, messages
from django.db import connection
from django.shortcuts import render, redirect
from django.urls import path


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="Fichier RBAC (CSV)")

# Extension de l'Admin pour ajouter le bouton d'import
@admin.register(admin.models.LogEntry)
class RBACAdmin(admin.ModelAdmin):
    change_list_template = "admin/rbac_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-rbac/', self.import_rbac),
        ]
        return my_urls + urls

    def import_rbac(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            try:
                # 🔴 Lire le fichier UNE SEULE FOIS en bytes
                csv_file.seek(0)
                file_content = csv_file.read()

                encodages = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                df = None

                # Essayer les encodages sur le contenu en bytes
                for encodage in encodages:
                    try:
                        from io import BytesIO
                        df = pd.read_csv(BytesIO(file_content), skiprows=9, encoding=encodage)
                        print(f"✓ Fichier lu avec {encodage}")
                        break
                    except Exception as e:
                        print(f"✗ {encodage}: {type(e).__name__}")
                        continue

                if df is None:
                    raise ValueError("Impossible de décoder le fichier. Encodages essayés : " + ", ".join(encodages))

                print(f"✓ DataFrame chargé: {len(df)} lignes, colonnes: {df.columns.tolist()}")

                roles = ["Expansion_L1", "Expansion_L2", "MRV_L1", "MRV_L2", "MRV_L3", "Admin_L1", "Admin_L2"]

                with connection.cursor() as cursor:
                    # ÉTAPE 0 : CRÉATION AUTOMATIQUE DES RÔLES
                    for role in roles:
                        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [role])
                        exists = cursor.fetchone()

                        if not exists:
                            cursor.execute(f'CREATE ROLE "{role}" NOLOGIN;')
                            cursor.execute(f'GRANT "{role}" TO authenticator;')

                    # ÉTAPE 1 : NETTOYAGE
                    for role in roles:
                        cursor.execute(f'REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM "{role}";')
                        cursor.execute(f'REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM "{role}";')

                    # ÉTAPE 2 : APPLICATION DE LA MATRICE
                    for _, row in df.iterrows():
                        table_name = str(row['Table']).strip()
                        if not table_name or table_name == 'nan':
                            continue

                        for role in roles:
                            perms = str(row[role]).strip()
                            if perms == '-' or perms == 'nan':
                                continue

                            actions = []
                            if 'C' in perms:
                                actions.append("INSERT")
                            if 'R' in perms:
                                actions.append("SELECT")
                            if 'U' in perms:
                                actions.append("UPDATE")
                            if 'D' in perms:
                                actions.append("DELETE")

                            if actions:
                                cursor.execute(f'GRANT {", ".join(actions)} ON TABLE {table_name} TO "{role}";')
                                if 'C' in perms:
                                    cursor.execute(
                                        f'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "{role}";')

                            if 'V' in perms:
                                cursor.execute(f'GRANT UPDATE (status_validation) ON TABLE {table_name} TO "{role}";')

                connection.commit()
                self.message_user(request, "✓ Succès : Rôles créés/vérifiés et matrice appliquée.")
                return redirect("..")

            except Exception as e:
                print(f"❌ ERREUR: {e}")
                import traceback
                traceback.print_exc()
                connection.rollback()
                self.message_user(request, f"❌ Erreur lors de l'import : {e}", level=messages.ERROR)

        form = CsvImportForm()
        return render(request, "admin/csv_form.html", {"form": form})

