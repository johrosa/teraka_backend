"""
Configuration du site admin personnalisé pour Teraka
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importer le site admin personnalisé
from core.admin_dashboard import teraka_admin

# Désenregistrer les modèles du site par défaut
from django.apps import apps
from django.contrib.gis import admin as gis_admin

# Enregistrer tous les modèles avec le bon admin
app_models = apps.get_app_config('core').get_models()

for model in app_models:
    try:
        # Utiliser GISModelAdmin pour les modèles géographiques
        if hasattr(model, 'geom') or hasattr(model, 'gps'):
            teraka_admin.register(model, gis_admin.GISModelAdmin)
        else:
            teraka_admin.register(model, admin.ModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass

# Enregistrer les modèles d'auth
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User, Group

class UserGroupInline(admin.TabularInline):
    model = User.groups.through
    extra = 1
    verbose_name = "Utilisateur"
    verbose_name_plural = "Utilisateurs"

class CustomGroupAdmin(GroupAdmin):
    inlines = [UserGroupInline]

teraka_admin.register(User)
try:
    teraka_admin.unregister(Group)
except admin.sites.NotRegistered:
    pass
teraka_admin.register(Group, CustomGroupAdmin)

# Enregistrer les autres apps si nécessaire
# teraka_admin.register(SomeOtherModel)

# Configuration des URLs pour le site admin personnalisé
teraka_admin_urls = [
    path('teraka/', teraka_admin.urls),
]

# Si vous voulez remplacer complètement l'admin par défaut
# admin.site = teraka_admin