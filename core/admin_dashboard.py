"""
Dashboard personnalisé pour l'admin Teraka
"""
from django.contrib import admin
from django.db import connection
from django.db.models import Count
from django.shortcuts import render
from django.urls import path
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from core.models_rbac import UserRole

User = get_user_model()


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
        from django.db.models import Avg, Sum
        from core.models import (
            Communes, BosquetBaseline, BosquetSuivi,
            ArbreBaseline, ArbreSuivi, Membre, PgInfos
        )

        # --- Dashboard Employés (Users & RBAC) ---
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()
        rbac_stats = UserRole.objects.values('role').annotate(count=Count('role')).order_by('role')

        # --- Dashboard Terrain (Suivi Agroforestier) ---
        communes_count = Communes.objects.count()
        membres_count = Membre.objects.count()
        pepiniere_count = Membre.objects.filter(pepinieriste=True).count()
        leader_count = Membre.objects.filter(leader=True).count()

        bosquets_count = BosquetBaseline.objects.count()
        bosquets_suivis = BosquetSuivi.objects.count()
        avg_survie = BosquetSuivi.objects.aggregate(Avg('taux_survie'))['taux_survie__avg'] or 0

        arbres_count = ArbreBaseline.objects.count()
        arbres_suivis = ArbreSuivi.objects.count()
        arbres_vivants = ArbreSuivi.objects.filter(statut_arbre='Vivant').count()

        pg_count = PgInfos.objects.count()
        pg_objectif_total = PgInfos.objects.aggregate(Sum('objectif_plantation_5_ans'))['objectif_plantation_5_ans__sum'] or 0

        # --- Activité Récente ---
        from django.contrib.admin.models import LogEntry
        from django.utils import timezone
        from datetime import timedelta

        last_7_days = timezone.now() - timedelta(days=7)
        recent_logs = LogEntry.objects.filter(action_time__gte=last_7_days).order_by('-action_time')[:10]

        context = {
            'title': 'Tableau de bord Teraka',

            # Employés
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'superuser_count': superuser_count,
            'rbac_stats': rbac_stats,
            'recent_logs': recent_logs,

            # Terrain
            'communes_count': communes_count,
            'membres_count': membres_count,
            'pepiniere_count': pepiniere_count,
            'leader_count': leader_count,
            'bosquets_count': bosquets_count,
            'bosquets_suivis': bosquets_suivis,
            'avg_survie': round(avg_survie, 2),
            'arbres_count': arbres_count,
            'arbres_suivis': arbres_suivis,
            'arbres_vivants': arbres_vivants,
            'pg_count': pg_count,
            'pg_objectif_total': pg_objectif_total,
        }

        return render(request, 'admin/teraka_dashboard.html', context)


# Instance du site admin personnalisé
teraka_admin = TerakaAdminSite(name='teraka_admin')
teraka_admin._registry.update(admin.site._registry)  # Copier les registrations existantes