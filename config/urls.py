"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from core.views import LoginForPostgrestView

from django.urls import re_path
from core.views import PostgrestProxyView

# Importer le dashboard personnalisé et les vues RBAC
from core.admin_dashboard import teraka_admin
from core.admin import RBACImportView, RBACStatusView
from core.views import rbac_hub_view

urlpatterns = [
    # IMPORTANT: Ces URLs RBAC doivent être AVANT admin.site.urls pour éviter le catch-all
    # Hub RBAC central
    path('admin/rbac/', rbac_hub_view, name='rbac_hub'),
    
    # URLs RBAC autonomes
    path('admin/rbac/import/', RBACImportView.as_view(), name='rbac_import'),
    path('admin/rbac/status/', RBACStatusView.as_view(), name='rbac_status'),
    
    # Dashboard Teraka personnalisé
    path('admin/dashboard/', teraka_admin.admin_view(teraka_admin.dashboard_view), name='teraka_dashboard'),
    
    # Admin Django (doit être APRÈS nos routes pour ne pas les intercepter)
    path('admin/', admin.site.urls),
    
    # C'est ici que le frontend se connectera pour avoir son Token
    path('api/login/', LoginForPostgrestView.as_view(), name='token_obtain_pair'),
    # Toutes les requêtes commençant par api/data/ iront vers PostgREST
    re_path(r'^api/data/(?P<path>.*)$', PostgrestProxyView.as_view(), name='postgrest_proxy'),
]

