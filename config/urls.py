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
from core.views import (
    home_page_view,
    profile_view,
    logout_view,
    LoginForPostgrestView,
    rbac_hub_view,
    platform_statistics_view,
    bosquet_statistics_view,
    data_validation_view,
    user_activity_log_view,
    system_health_view,
    members_by_region_view,
    data_quality_report_view,
    data_export_view,
    audit_log_view,
    audit_hash_verify_view,
)

from django.urls import re_path
from core.views import PostgrestProxyView

# Importer le dashboard personnalisé et les vues RBAC
from core.admin_dashboard import teraka_admin
from core.admin import RBACImportView, RBACStatusView

urlpatterns = [
    # ============================================================================
    # HOME PAGE
    # ============================================================================
    path('', home_page_view, name='home'),
    path('accounts/profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    
    # IMPORTANT: Ces URLs RBAC doivent être AVANT admin.site.urls pour éviter le catch-all
    # Hub RBAC central
    path('admin/rbac/', rbac_hub_view, name='rbac_hub'),
    
    # URLs RBAC autonomes
    path('admin/rbac/import/', RBACImportView.as_view(), name='rbac_import'),
    path('admin/rbac/status/', RBACStatusView.as_view(), name='rbac_status'),
    
    # Audit Log URLs
    path('admin/audit/', audit_log_view, name='audit_log'),
    path('api/audit/verify/', audit_hash_verify_view, name='audit_hash_verify'),
    
    # Dashboard Teraka personnalisé
    path('admin/dashboard/', teraka_admin.admin_view(teraka_admin.dashboard_view), name='teraka_dashboard'),
    path('admin/logout/', logout_view, name='admin_logout'),
    
    # Admin Django (doit être APRÈS nos routes pour ne pas les intercepter)
    path('admin/', admin.site.urls),
    
    # ============================================================================
    # API ENDPOINTS - Gestion et Statistiques
    # ============================================================================
    
    # C'est ici que le frontend se connectera pour avoir son Token
    path('api/login/', LoginForPostgrestView.as_view(), name='token_obtain_pair'),
    
    # API de gestion et statistiques (admin uniquement)
    path('api/statistics/', platform_statistics_view, name='api_statistics'),
    path('api/bosquet-statistics/', bosquet_statistics_view, name='api_bosquet_stats'),
    path('api/data-validation/', data_validation_view, name='api_data_validation'),
    path('api/user-activity/', user_activity_log_view, name='api_user_activity'),
    path('api/system-health/', system_health_view, name='api_system_health'),
    path('api/members-by-region/', members_by_region_view, name='api_members_region'),
    path('api/data-quality/', data_quality_report_view, name='api_data_quality'),
    path('api/export/', data_export_view, name='api_export'),
    
    # Toutes les requêtes commençant par api/data/ iront vers PostgREST
    re_path(r'^api/data/(?P<path>.*)$', PostgrestProxyView.as_view(), name='postgrest_proxy'),
]

