"""
Dashboard personnalisé pour l'admin Teraka
"""
from django.contrib import admin
from django.db import connection
from django.db.models import Count, F
from django.shortcuts import render
from django.urls import path
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from core.models_rbac import UserRole


class TerakaAdminSite(admin.AdminSite):
    """Site admin personnalisé pour Teraka"""

    site_header = "Administration Teraka Platform"
    site_title = "Teraka Admin"
    index_title = "Tableau de bord Teraka"
    site_url = None  # Désactiver le lien vers le site

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='teraka_dashboard'),
        ]
        return custom_urls + urls

    @method_decorator(staff_member_required)
    def dashboard_view(self, request):
        """Vue du dashboard personnalisé"""

        # Statistiques utilisateurs et rôles
        User = get_user_model()
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()

        # Statistiques RBAC
        rbac_stats = (
            UserRole.objects
            .values(role_code=F('role__code'))
            .annotate(count=Count('role'))
            .order_by('role_code')
        )

        # Statistiques base de données (tables principales)
        with connection.cursor() as cursor:
            # Communes
            cursor.execute("SELECT COUNT(*) FROM communes")
            communes_count = cursor.fetchone()[0]

            # Bosquets
            cursor.execute("SELECT COUNT(*) FROM bosquet_suivi")
            bosquets_count = cursor.fetchone()[0]

            # Membres
            cursor.execute("SELECT COUNT(*) FROM membre")
            membres_count = cursor.fetchone()[0]

            # Arbres
            cursor.execute("SELECT COUNT(*) FROM arbre_suivi")
            arbres_count = cursor.fetchone()[0]

        context = {
            'title': 'Tableau de bord Teraka',
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'superuser_count': superuser_count,
            'rbac_stats': rbac_stats,
            'communes_count': communes_count,
            'bosquets_count': bosquets_count,
            'membres_count': membres_count,
            'arbres_count': arbres_count,
        }

        return render(request, 'admin/teraka_dashboard.html', context)


# Instance du site admin personnalisé
teraka_admin = TerakaAdminSite(name='teraka_admin')
teraka_admin._registry.update(admin.site._registry)  # Copier les registrations existantes
