from django.contrib.gis import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.apps import apps
from core.models import (
    Membre, ArbreBaseline, ArbreSuivi, BosquetBaseline, BosquetSuivi,
    PgInfos, Communes, EspecesArbres, Users, AuditLog
)
from core.models_rbac import UserRole

# --- Configuration spécialisée pour les modèles clés ---

@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom_membre', 'c_com', 'statut_membre', 'genre', 'annee_inscription', 'pepinieriste', 'leader')
    list_filter = ('statut_membre', 'genre', 'pepinieriste', 'leader', 'c_com')
    search_fields = ('nom_membre', 'prenom_membre', 'cin', 'tel', 'code_pg')
    list_per_page = 20

@admin.register(ArbreBaseline)
class ArbreBaselineAdmin(admin.ModelAdmin):
    list_display = ('uuid_arbre_baseline', 'uuid_espece', 'c_com', 'date_baseline', 'age', 'statut_arbre_gps')
    list_filter = ('uuid_espece', 'c_com', 'date_baseline')
    search_fields = ('uuid_arbre_baseline', 'autre_espece')

    def statut_arbre_gps(self, obj):
        return obj.uuid_arbre_gps.statut_arbre if obj.uuid_arbre_gps else "-"
    statut_arbre_gps.short_description = "Statut GPS"

@admin.register(ArbreSuivi)
class ArbreSuiviAdmin(admin.ModelAdmin):
    list_display = ('uuid_arbre_suivi', 'uuid_espece', 'statut_arbre', 'hauteur', 'circonference', 'date_suivi')
    list_filter = ('statut_arbre', 'uuid_espece', 'date_suivi', 'c_com')
    search_fields = ('uuid_arbre_suivi', 'remarque')

@admin.register(BosquetBaseline)
class BosquetBaselineAdmin(admin.GISModelAdmin):
    list_display = ('uuid_bosquet_baseline', 'nom_proprietaire', 'c_com', 'surface_boisee_ha', 'date_baseline')
    list_filter = ('c_com', 'proprietaire', 'conflit_foncier', 'date_baseline')
    search_fields = ('nom_proprietaire', 'uuid_bosquet_baseline')
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 12,
            'map_width': 800,
            'map_height': 500,
        }
    }

@admin.register(BosquetSuivi)
class BosquetSuiviAdmin(admin.ModelAdmin):
    list_display = ('uuid_bosquet_suivi', 'uuid_bosquet_gps', 'taux_survie', 'date_suivi', 'c_com')
    list_filter = ('c_com', 'date_suivi')
    search_fields = ('uuid_bosquet_suivi',)

@admin.register(PgInfos)
class PgInfosAdmin(admin.ModelAdmin):
    list_display = ('nom_pg', 'code_pg', 'statut_pg', 'c_com', 'annee_inscription')
    list_filter = ('statut_pg', 'annee_inscription', 'c_com')
    search_fields = ('nom_pg', 'code_pg', 'representant_pg')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_name', 'operation', 'user_id', 'action_time', 'record_id')
    list_filter = ('operation', 'table_name', 'action_time')
    search_fields = ('table_name', 'record_id', 'user_id', 'operation')
    readonly_fields = ('id', 'table_name', 'operation', 'record_id', 'user_id', 'action_time', 
                       'old_data', 'new_data', 'previous_hash', 'current_hash')
    list_per_page = 50
    date_hierarchy = 'action_time'
    
    def has_add_permission(self, request):
        """Les logs ne peuvent pas être ajoutés manuellement"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Seuls les superusers peuvent supprimer les logs"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Les logs sont read-only"""
        return False

# --- Enregistrement dynamique pour les autres modèles ---

app_models = apps.get_app_config('core').get_models()

# Exclure les modèles déjà enregistrés
excluded_models = {
    UserRole, Membre, ArbreBaseline, ArbreSuivi,
    BosquetBaseline, BosquetSuivi, PgInfos
}

for model in app_models:
    if model in excluded_models:
        continue
    
    try:
        # On crée une classe qui hérite de GISModelAdmin pour le support spatial
        @admin.register(model)
        class DynamicGeoAdmin(admin.GISModelAdmin):
            # Essayer d'afficher les 5 premiers champs pour éviter des listes trop larges
            list_display = [field.name for field in model._meta.fields[:6]]

            # Paramètres pour l'affichage de la carte si champ geom présent
            gis_widget_kwargs = {
                'attrs': {
                    'default_zoom': 11,
                    'scrollable': True,
                    'map_width': 700,
                    'map_height': 400,
                }
            }
    except (AlreadyRegistered, TypeError):
        pass



import pandas as pd
from io import BytesIO, TextIOWrapper
from django import forms
from django.contrib import admin, messages
from django.db import connection
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="Fichier RBAC (CSV)")


class RBACImportView(View):
    """Vue pour importer la matrice RBAC"""

    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Afficher le formulaire d'import"""
        form = CsvImportForm()
        return render(request, "admin/csv_form.html", {"form": form})

    def post(self, request):
        """Traiter l'upload du fichier"""
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.error(request, "Aucun fichier sélectionné")
            return render(request, "admin/csv_form.html", {"form": CsvImportForm()})

        try:
            csv_file.seek(0)
            file_content = csv_file.read()

            encodages = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            separateurs = [None, ';', ',', '\t']
            df = None
            erreurs = []

            if not file_content:
                raise ValueError("Le fichier est vide.")

            is_excel = csv_file.name.lower().endswith(('.xls', '.xlsx')) or file_content[:2] == b'PK'

            if is_excel:
                try:
                    df = pd.read_excel(
                        BytesIO(file_content),
                        skiprows=8,
                    )
                    print(f"[OK] Fichier Excel lu avec read_excel, colonnes={df.columns.tolist()}")
                except Exception as e:
                    erreurs.append(f"excel: {type(e).__name__}: {e}")
            else:
                for encodage in encodages:
                    for sep in separateurs:
                        try:
                            stream = TextIOWrapper(
                                BytesIO(file_content),
                                encoding=encodage,
                                newline='',
                            )
                            df = pd.read_csv(
                                stream,
                                skiprows=8,
                                sep=sep,
                                engine='python',
                                quotechar='"',
                                escapechar='\\',
                                keep_default_na=False,
                            )
                            print(f"[OK] Fichier lu avec {encodage}, separateur={sep or 'auto'}")
                            break
                        except UnicodeDecodeError as e:
                            erreurs.append(f"{encodage}: {e}")
                        except Exception as e:
                            erreurs.append(f"{encodage} sep={sep or 'auto'}: {type(e).__name__}: {e}")
                        finally:
                            try:
                                stream.close()
                            except Exception:
                                pass

                    if df is not None:
                        break

            if df is None:
                raise ValueError(
                    "Impossible de lire le fichier. Encodages/format(s) essayes : "
                    + " ; ".join(erreurs)
                )

            print(f"[OK] DataFrame charge: {len(df)} lignes, colonnes: {df.columns.tolist()}")

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
                            # Vérifier si la colonne "status_validation" existe
                            cursor.execute("""
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_name = %s AND column_name = 'status_validation'
                            """, [table_name])

                            if cursor.fetchone():
                                cursor.execute(f'GRANT UPDATE (status_validation) ON TABLE {table_name} TO "{role}";')
                            else:
                                print(f"[AVERTISSEMENT] Colonne 'status_validation' non trouvée dans la table '{table_name}' - permission V ignorée pour le rôle '{role}'")

            connection.commit()
            messages.success(request, "✅ Roles créés/vérifiés et matrice appliquée.")
            return redirect('/admin/')

        except Exception as e:
            print(f"[ERREUR] {e}")
            import traceback
            traceback.print_exc()
            connection.rollback()
            messages.error(request, f"❌ Erreur lors de l'import : {e}")
            return render(request, "admin/csv_form.html", {"form": CsvImportForm()})


class RBACStatusView(View):
    """Vue pour afficher le statut actuel des permissions RBAC"""

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Afficher le statut RBAC"""
        with connection.cursor() as cursor:
            # Rôles existants
            cursor.execute("SELECT rolname FROM pg_roles WHERE rolname LIKE '%_L%' ORDER BY rolname")
            roles = [row[0] for row in cursor.fetchall()]

            # Permissions par rôle et table
            permissions_data = []
            for role in roles:
                cursor.execute("""
                    SELECT table_name, privilege_type
                    FROM information_schema.role_table_grants
                    WHERE grantee = %s AND table_schema = 'public'
                    ORDER BY table_name, privilege_type
                """, [role])

                role_permissions = {}
                for row in cursor.fetchall():
                    table, privilege = row
                    if table not in role_permissions:
                        role_permissions[table] = []
                    role_permissions[table].append(privilege)

                permissions_data.append({
                    'role': role,
                    'permissions': role_permissions
                })

        context = {
            'permissions_data': permissions_data,
            'roles': roles,
        }

        return render(request, "admin/rbac_status.html", context)


# Admin pour les associations Utilisateur-Rôle
# (UserRole est importé au-dessus pour être exclu de la boucle dynamique)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_role_display', 'get_role_description', 'created_at', 'updated_at', 'is_active_user']
    list_filter = ['created_at', 'updated_at', 'user__is_active']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['user__username']
    list_per_page = 25

    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',),
            'description': 'Sélectionnez l\'utilisateur Django à associer à un rôle.'
        }),
        ('Rôle PostgreSQL', {
            'fields': ('role_select',),
            'description': 'Sélectionnez le rôle PostgreSQL qui sera utilisé pour les permissions PostgREST.'
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at', 'is_active_user'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'is_active_user']

    def get_form(self, request, obj=None, **kwargs):
        """Ajoute un champ de sélection pour le rôle qui n'est plus dans le modèle"""
        form_class = super().get_form(request, obj, **kwargs)

        # On définit une classe interne pour ne pas modifier la classe parente
        class UserRoleForm(form_class):
            role_select = forms.ChoiceField(
                choices=UserRole.POSTGRES_ROLES,
                label="Rôle PostgreSQL",
                required=True
            )

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if self.instance and self.instance.pk:
                    self.fields['role_select'].initial = self.instance.role

        return UserRoleForm

    def get_role_display(self, obj):
        """Affiche le rôle actuel (propriété)"""
        return obj.role or "Aucun rôle"
    get_role_display.short_description = 'Rôle'

    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related('user')

    def get_role_description(self, obj):
        """Afficher la description du rôle"""
        descriptions = {
            'Expansion_L1': 'Création seulement',
            'Expansion_L2': 'Lecture + Modification',
            'MRV_L1': 'Lecture seule',
            'MRV_L2': 'Lecture + Modification',
            'MRV_L3': 'Lecture + Modification + Validation',
            'Admin_L1': 'Lecture + Modification',
            'Admin_L2': 'Lecture + Modification + Suppression',
        }
        return descriptions.get(obj.role, obj.role)
    get_role_description.short_description = 'Description du rôle'
    get_role_description.admin_order_field = 'role'

    def is_active_user(self, obj):
        """Indiquer si l'utilisateur est actif"""
        return obj.user.is_active
    is_active_user.boolean = True
    is_active_user.short_description = 'Utilisateur actif'

    def save_model(self, request, obj, form, change):
        """
        Override pour ajouter des validations et messages
        """
        from django.contrib import messages
        
        # Vérifier qu'un utilisateur n'a qu'un seul rôle
        if not change:  # Nouvelle création
            existing = UserRole.objects.filter(user=obj.user).exclude(pk=obj.pk)
            if existing.exists():
                messages.error(
                    request,
                    f"L'utilisateur '{obj.user.username}' a déjà un rôle assigné. "
                    f"Modifiez l'existant au lieu d'en créer un nouveau."
                )
                return

        # On récupère le rôle depuis le champ personnalisé du formulaire
        role_name = form.cleaned_data.get('role_select')
        obj.role = role_name  # Utilise le setter de la propriété dans models_rbac.py

        super().save_model(request, obj, form, change)

        if not change:  # Nouvelle création
            self.message_user(
                request,
                f"✅ L'utilisateur '{obj.user.username}' a été associé au rôle '{role_name}'.",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                f"✅ Le rôle de '{obj.user.username}' a été mis à jour en '{role_name}'.",
                level=messages.SUCCESS
            )

    def has_delete_permission(self, request, obj=None):
        """Permettre la suppression seulement aux superusers"""
        if request.user.is_superuser:
            return True
        return False

    class Media:
        css = {
            'all': ('admin/css/userrole_admin.css',)
        }

