from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import PostgrestTokenSerializer


class LoginForPostgrestView(TokenObtainPairView):
    serializer_class = PostgrestTokenSerializer


from revproxy.views import ProxyView
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication

class PostgrestProxyView(ProxyView):
    # L'adresse interne où tourne PostgREST (non publiée sur le web)
    upstream = 'http://127.0.0.1:3000'

    def dispatch(self, request, *args, **kwargs):
        # On tente l'authentification via JWT si l'utilisateur n'est pas déjà authentifié par session
        if not request.user.is_authenticated:
            try:
                auth_header = JWTAuthentication().authenticate(request)
                if auth_header:
                    request.user, _ = auth_header
            except Exception:
                pass

        # Vérification manuelle de l'authentification car ProxyView n'est pas une APIView de DRF
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentification requise."}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def get_proxy_request_headers(self, request):
        headers = super().get_proxy_request_headers(request)
        # On peut ici ajouter ou modifier des headers si besoin
        return headers


# ============================================================================
# RBAC HUB - Page centrale pour gérer les permissions RBAC
# ============================================================================

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods


@staff_member_required
@require_http_methods(["GET"])
def rbac_hub_view(request):
    """
    Hub central RBAC - Page d'accueil pour gérer les rôles et permissions
    Accessible uniquement aux administrateurs.
    """
    context = {
        'title': 'RBAC - Gestion des permissions',
        'site_header': 'Administration Teraka',
        'site_title': 'Teraka Platform',
    }
    return render(request, 'admin/rbac_hub.html', context)


# ============================================================================
# API VIEWS - Vues pour les API REST de gestion
# ============================================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
import json


@api_view(['GET'])
@permission_classes([IsAdminUser])
def platform_statistics_view(request):
    """
    Récupère les statistiques globales de la plateforme
    """
    try:
        from core.models import (
            BosquetBaseline, BosquetSuivi, ArbreBaseline, ArbreSuivi,
            Membre, MembreSuivi, Communes, PgInfos, PgSuivi
        )
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        stats = {
            'timestamp': now.isoformat(),
            'platform': {
                'total_communes': Communes.objects.count(),
                'total_bosquets': BosquetBaseline.objects.count(),
                'total_arbres': ArbreBaseline.objects.count(),
                'total_membres': Membre.objects.count(),
                'total_pg': PgInfos.objects.count(),
            },
            'suivi': {
                'bosquets_suivi': BosquetSuivi.objects.count(),
                'arbres_suivi': ArbreSuivi.objects.count(),
                'membres_suivi': MembreSuivi.objects.count(),
                'pg_suivi': PgSuivi.objects.count(),
            },
            'recent_activity': {
                'bosquets_last_30d': BosquetSuivi.objects.filter(
                    created_at__gte=last_30_days
                ).count(),
                'arbres_last_30d': ArbreSuivi.objects.filter(
                    created_at__gte=last_30_days
                ).count(),
                'membres_last_30d': MembreSuivi.objects.filter(
                    created_at__gte=last_30_days
                ).count(),
            }
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def bosquet_statistics_view(request):
    """
    Statistiques détaillées par bosquet avec historique
    """
    try:
        from core.models import BosquetBaseline, BosquetSuivi
        
        bosquets = BosquetBaseline.objects.all().values('uuid_bosquet_baseline', 'c_com')
        
        stats_list = []
        for bosquet in bosquets:
            bosquet_id = bosquet['uuid_bosquet_baseline']
            suivi_count = BosquetSuivi.objects.filter(
                uuid_bosquet_baseline=bosquet_id
            ).count()
            
            stats_list.append({
                'bosquet_id': str(bosquet_id),
                'commune': bosquet['c_com'],
                'suivi_count': suivi_count,
            })
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'bosquets_count': len(stats_list),
            'data': stats_list
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def data_validation_view(request):
    """
    Valide l'intégrité des données et retourne les erreurs potentielles
    """
    try:
        from core.models import (
            BosquetBaseline, BosquetSuivi, ArbreBaseline, ArbreSuivi,
            Membre, MembreSuivi
        )
        
        validation_errors = {
            'timestamp': timezone.now().isoformat(),
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        # Vérifier les bosquets sans arbres
        bosquets_sans_arbres = BosquetBaseline.objects.annotate(
            arbre_count=Count('arbrebaseline')
        ).filter(arbre_count=0).count()
        
        if bosquets_sans_arbres > 0:
            validation_errors['warnings'].append({
                'type': 'bosquets_sans_arbres',
                'count': bosquets_sans_arbres,
                'message': f'{bosquets_sans_arbres} bosquets sans arbres enregistrés'
            })
        
        # Vérifier les arbres sans bosquet
        arbres_orphelins = ArbreBaseline.objects.filter(
            uuid_bosquet_baseline__isnull=True
        ).count()
        
        if arbres_orphelins > 0:
            validation_errors['errors'].append({
                'type': 'arbres_orphelins',
                'count': arbres_orphelins,
                'message': f'{arbres_orphelins} arbres sans bosquet'
            })
        
        # Vérifier les membres sans commune
        membres_sans_commune = Membre.objects.filter(
            c_com__isnull=True
        ).count()
        
        if membres_sans_commune > 0:
            validation_errors['warnings'].append({
                'type': 'membres_sans_commune',
                'count': membres_sans_commune,
                'message': f'{membres_sans_commune} membres sans commune'
            })
        
        validation_errors['summary'] = {
            'total_errors': len(validation_errors['errors']),
            'total_warnings': len(validation_errors['warnings']),
            'critical': len(validation_errors['errors']) > 0
        }
        
        return Response(validation_errors, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_activity_log_view(request):
    """
    Affiche le journal d'activité des utilisateurs (dernières 30 jours)
    """
    try:
        from django.contrib.admin.models import LogEntry
        
        last_30_days = timezone.now() - timedelta(days=30)
        
        logs = LogEntry.objects.filter(
            action_time__gte=last_30_days
        ).values(
            'user__username',
            'content_type__model',
            'action_flag',
            'action_time'
        ).order_by('-action_time')[:100]
        
        action_names = {1: 'CREATE', 2: 'EDIT', 3: 'DELETE'}
        
        logs_list = []
        for log in logs:
            logs_list.append({
                'username': log['user__username'],
                'model': log['content_type__model'],
                'action': action_names.get(log['action_flag'], 'UNKNOWN'),
                'timestamp': log['action_time'].isoformat()
            })
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'logs_count': len(logs_list),
            'data': logs_list
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health_view(request):
    """
    Vérifie la santé du système (BD, cache, etc.)
    """
    try:
        from django.db import connection
        import os
        
        health = {
            'timestamp': timezone.now().isoformat(),
            'status': 'healthy',
            'checks': {}
        }
        
        # Vérifier la base de données
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            health['checks']['database'] = {
                'status': 'ok',
                'message': 'Base de données accessible'
            }
        except Exception as e:
            health['checks']['database'] = {
                'status': 'error',
                'message': str(e)
            }
            health['status'] = 'unhealthy'
        
        # Vérifier l'espace disque
        try:
            import shutil
            disk_usage = shutil.disk_usage('/')
            percent_used = (disk_usage.used / disk_usage.total) * 100
            
            health['checks']['disk_space'] = {
                'status': 'ok' if percent_used < 90 else 'warning',
                'used_gb': disk_usage.used / (1024**3),
                'total_gb': disk_usage.total / (1024**3),
                'percent_used': percent_used
            }
        except Exception as e:
            health['checks']['disk_space'] = {
                'status': 'unknown',
                'message': str(e)
            }
        
        # Vérifier les fichiers statiques
        static_path = os.path.join(os.path.dirname(__file__), '../static')
        health['checks']['static_files'] = {
            'status': 'ok' if os.path.exists(static_path) else 'missing',
            'path': static_path
        }
        
        return Response(health, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e), 'status': 'error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def members_by_region_view(request):
    """
    Récupère les statistiques des membres par région/commune
    """
    try:
        from core.models import Membre, Communes
        
        communes = Communes.objects.all().values('c_com', 'nom_commun')
        
        regions_data = []
        for commune in communes:
            members_count = Membre.objects.filter(
                c_com=commune['c_com']
            ).count()
            
            regions_data.append({
                'commune_code': commune['c_com'],
                'commune_name': commune['nom_commun'],
                'members_count': members_count
            })
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'total_communes': len(regions_data),
            'data': sorted(regions_data, key=lambda x: x['members_count'], reverse=True)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def data_quality_report_view(request):
    """
    Génère un rapport de qualité des données
    """
    try:
        from core.models import (
            BosquetBaseline, BosquetSuivi, ArbreBaseline, ArbreSuivi,
            Membre, MembreSuivi, PgInfos, PgSuivi
        )
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'data_completeness': {},
            'data_freshness': {},
            'quality_score': 0
        }
        
        # Complétude des données
        bosquet_total = BosquetBaseline.objects.count()
        bosquet_with_suivi = BosquetSuivi.objects.count()
        
        report['data_completeness'] = {
            'bosquets': {
                'baseline': bosquet_total,
                'suivi': bosquet_with_suivi,
                'coverage_percent': (bosquet_with_suivi / bosquet_total * 100) if bosquet_total > 0 else 0
            },
            'arbres': {
                'baseline': ArbreBaseline.objects.count(),
                'suivi': ArbreSuivi.objects.count(),
            },
            'membres': {
                'total': Membre.objects.count(),
                'suivi': MembreSuivi.objects.count(),
            }
        }
        
        # Fraîcheur des données (dernière mise à jour)
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        
        report['data_freshness'] = {
            'bosquet_suivi_last_7d': BosquetSuivi.objects.filter(
                updated_at__gte=last_7_days
            ).count(),
            'arbre_suivi_last_7d': ArbreSuivi.objects.filter(
                updated_at__gte=last_7_days
            ).count(),
        }
        
        # Score de qualité (0-100)
        coverage = report['data_completeness']['bosquets']['coverage_percent']
        freshness_score = min(100, report['data_freshness']['bosquet_suivi_last_7d'] * 10)
        report['quality_score'] = int((coverage + freshness_score) / 2)
        
        return Response(report, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def data_export_view(request):
    """
    Exporte les données en JSON ou CSV
    Format: request.data = {'format': 'json'|'csv', 'tables': ['bosquets', 'arbres', ...]}
    """
    try:
        export_format = request.data.get('format', 'json')
        tables = request.data.get('tables', ['bosquets', 'arbres', 'membres'])
        
        export_data = {
            'timestamp': timezone.now().isoformat(),
            'format': export_format,
            'tables': {}
        }
        
        if 'bosquets' in tables:
            from core.models import BosquetBaseline
            bosquets = list(BosquetBaseline.objects.values())
            export_data['tables']['bosquets'] = {
                'count': len(bosquets),
                'data': bosquets[:100]  # Limiter à 100 pour la réponse API
            }
        
        if 'arbres' in tables:
            from core.models import ArbreBaseline
            arbres = list(ArbreBaseline.objects.values())
            export_data['tables']['arbres'] = {
                'count': len(arbres),
                'data': arbres[:100]
            }
        
        if 'membres' in tables:
            from core.models import Membre
            membres = list(Membre.objects.values())
            export_data['tables']['membres'] = {
                'count': len(membres),
                'data': membres[:100]
            }
        
        return Response(export_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )