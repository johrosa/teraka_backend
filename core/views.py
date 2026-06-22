# ============================================================================
# AUDIT LOG VIEW - Tamper-evident audit trail visualization
# ============================================================================

from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse
from datetime import datetime, timedelta


@login_required
@staff_member_required
@require_http_methods(["GET"])
def audit_log_view(request):
    """
    Display tamper-evident audit log with filtering and search.
    
    Filters:
    - table_name: filter by table
    - operation: INSERT, UPDATE, DELETE
    - changed_by: filter by user email
    - date_from: start date (YYYY-MM-DD)
    - date_to: end date (YYYY-MM-DD)
    - search: search in table/email
    
    Verifies hash chain integrity by recomputing hashes.
    """
    try:
        # Get filter parameters
        table_name_filter = request.GET.get('table', '').strip()
        operation_filter = request.GET.get('operation', '').strip()
        changed_by_filter = request.GET.get('changed_by', '').strip()
        date_from = request.GET.get('date_from', '').strip()
        date_to = request.GET.get('date_to', '').strip()
        search_query = request.GET.get('search', '').strip()
        page_num = request.GET.get('page', 1)
        
        # Build SQL query
        sql = "SELECT * FROM public.audit_log_view WHERE 1=1"
        params = []
        
        if table_name_filter:
            sql += " AND table_name = %s"
            params.append(table_name_filter)
        
        if operation_filter:
            sql += " AND operation = %s"
            params.append(operation_filter)
        
        if changed_by_filter:
            sql += " AND (changed_by_email ILIKE %s OR changed_by = %s)"
            params.extend([f"%{changed_by_filter}%", changed_by_filter])
        
        if search_query:
            sql += " AND (table_name ILIKE %s OR changed_by_email ILIKE %s)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        
        if date_from:
            sql += " AND event_time::date >= %s"
            params.append(date_from)
        
        if date_to:
            sql += " AND event_time::date <= %s"
            params.append(date_to)
        
        sql += " ORDER BY id DESC"
        
        # Execute query
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        
        # Convert to list of dicts
        audit_entries = [dict(zip(columns, row)) for row in rows]
        
        # Format dates for display
        for entry in audit_entries:
            if entry.get('event_time'):
                entry['event_time_formatted'] = entry['event_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Pagination
        paginator = Paginator(audit_entries, 50)
        page_obj = paginator.get_page(page_num)
        
        # Get unique tables for filter dropdown
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT table_name FROM public.audit_log_view 
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        # Get unique changed_by for filter dropdown
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT changed_by_email FROM public.audit_log_view 
                WHERE changed_by_email IS NOT NULL
                ORDER BY changed_by_email
            """)
            users = [row[0] for row in cursor.fetchall()]
        
        context = {
            'page_obj': page_obj,
            'audit_entries': page_obj.object_list,
            'tables': tables,
            'users': users,
            'filters': {
                'table': table_name_filter,
                'operation': operation_filter,
                'changed_by': changed_by_filter,
                'date_from': date_from,
                'date_to': date_to,
                'search': search_query,
            },
            'total_count': len(audit_entries),
            'has_filters': bool(table_name_filter or operation_filter or changed_by_filter or date_from or date_to or search_query),
        }
        
        return render(request, 'admin/audit_log_view.html', context)
    
    except Exception as e:
        import traceback
        context = {
            'error': str(e),
            'traceback': traceback.format_exc(),
        }
        return render(request, 'admin/audit_log_view.html', context, status=500)


@login_required
@staff_member_required
@require_http_methods(["GET"])
def audit_hash_verify_view(request):
    """
    Verify audit log hash chain integrity.
    Returns JSON with verification results.
    """
    try:
        table_filter = request.GET.get('table', '').strip()
        
        with connection.cursor() as cursor:
            # Get all audit entries for the table
            if table_filter:
                cursor.execute("""
                    SELECT id, prev_hash, row_hash, event_time, operation, 
                           encode(digest(coalesce(prev_hash,'') || (jsonb_build_object('op', operation, 
                           'schema', schema_name, 'table', table_name, 'data', row_data, 
                           'txid', txid, 'actor', changed_by)::text) || event_time::text, 'sha256'), 'hex') AS recomputed
                    FROM public.audit_log
                    WHERE table_name = %s
                    ORDER BY id
                """, [table_filter])
            else:
                cursor.execute("""
                    SELECT id, prev_hash, row_hash, event_time, operation,
                           encode(digest(coalesce(prev_hash,'') || (jsonb_build_object('op', operation, 
                           'schema', schema_name, 'table', table_name, 'data', row_data, 
                           'txid', txid, 'actor', changed_by)::text) || event_time::text, 'sha256'), 'hex') AS recomputed
                    FROM public.audit_log
                    ORDER BY id
                """)
            
            rows = cursor.fetchall()
        
        # Check integrity
        verification = []
        all_valid = True
        for row_id, prev_hash, stored_hash, event_time, operation, recomputed_hash in rows:
            is_valid = stored_hash == recomputed_hash
            verification.append({
                'id': row_id,
                'valid': is_valid,
                'operation': operation,
                'event_time': event_time.isoformat(),
            })
            if not is_valid:
                all_valid = False
        
        return JsonResponse({
            'status': 'success',
            'chain_intact': all_valid,
            'entries_checked': len(verification),
            'invalid_count': sum(1 for v in verification if not v['valid']),
            'verification': verification,
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


# ============================================================================
# HOME PAGE - Page d'accueil de la plateforme
# ============================================================================


@require_http_methods(["GET", "HEAD"])
def home_page_view(request):
    """
    Page d'accueil de la plateforme Teraka
    Affiche un dashboard public avec statistiques rapides
    """
    try:
        from core.models import (
            Communes, BosquetBaseline, BosquetSuivi,
            ArbreBaseline, ArbreSuivi, Membre, MembreSuivi,
            PgInfos, PgSuivi
        )
        
        context = {
            'title': 'Teraka Platform - Suivi Agroforestier',
            'site_header': 'Teraka Platform',
            'site_title': 'Teraka',
            
            # Statistiques globales
            'communes_count': Communes.objects.count(),
            'bosquets_total': BosquetBaseline.objects.count(),
            'bosquets_suivi': BosquetSuivi.objects.count(),
            'arbres_total': ArbreBaseline.objects.count(),
            'arbres_suivi': ArbreSuivi.objects.count(),
            'membres_total': Membre.objects.count(),
            'membres_suivi': MembreSuivi.objects.count(),
            'pg_total': PgInfos.objects.count(),
            'pg_suivi': PgSuivi.objects.count(),
            
            # Calculs
            'bosquets_coverage': (
                (BosquetSuivi.objects.count() / BosquetBaseline.objects.count() * 100)
                if BosquetBaseline.objects.count() > 0 else 0
            ),
            'arbres_coverage': (
                (ArbreSuivi.objects.count() / ArbreBaseline.objects.count() * 100)
                if ArbreBaseline.objects.count() > 0 else 0
            ),
            'membres_coverage': (
                (MembreSuivi.objects.count() / Membre.objects.count() * 100)
                if Membre.objects.count() > 0 else 0
            ),
            'is_authenticated': request.user.is_authenticated,
            'is_admin': request.user.is_superuser if request.user.is_authenticated else False,
        }
        
        return render(request, 'home.html', context)
    
    except Exception as e:
        # En cas d'erreur, afficher une page simple
        context = {
            'title': 'Teraka Platform',
            'error': str(e),
            'is_authenticated': request.user.is_authenticated,
        }
        return render(request, 'home.html', context)


@login_required
@require_http_methods(["GET"])
def profile_view(request):
    """
    Page de profil et dashboard utilisée comme redirection post-login Django.
    """
    user = request.user
    user_uuid = getattr(user, 'uuid_user', None)
    user_role = getattr(user, 'role', '') or ''
    postgres_role = getattr(user, 'postgres_role', None)
    postgres_role_obj = getattr(postgres_role, 'role', None)
    postgres_role_code = getattr(postgres_role_obj, 'code', '') or user_role
    postgres_role_description = getattr(postgres_role_obj, 'description', '')
    commune = getattr(user, 'c_com', None)
    commune_name = getattr(commune, 'nom_commun', '') or getattr(user, 'c_com_id', '')
    full_name = ' '.join(
        part for part in [
            getattr(user, 'prenom', '') or '',
            getattr(user, 'nom', '') or '',
        ]
        if part
    )

    dashboard = {
        'communes_count': 0,
        'bosquets_total': 0,
        'arbres_total': 0,
        'membres_total': 0,
        'pg_total': 0,
        'suivi_pg_total': 0,
        'my_pg_count': 0,
        'my_pending_pg_count': 0,
        'my_bosquets_count': 0,
        'my_membres_count': 0,
        'my_validations_count': 0,
    }

    try:
        from core.models import (
            Communes, BosquetBaseline, ArbreBaseline, Membre, PgInfos, PgSuivi
        )

        dashboard.update({
            'communes_count': Communes.objects.count(),
            'bosquets_total': BosquetBaseline.objects.count(),
            'arbres_total': ArbreBaseline.objects.count(),
            'membres_total': Membre.objects.count(),
            'pg_total': PgInfos.objects.count(),
            'suivi_pg_total': PgSuivi.objects.count(),
        })

        if user_uuid:
            my_pg = PgInfos.objects.filter(uuid_operateur=user_uuid)
            dashboard['my_pg_count'] = my_pg.count()
            dashboard['my_pending_pg_count'] = my_pg.filter(
                date_verification__isnull=True
            ).count()
            dashboard['my_validations_count'] = PgInfos.objects.filter(
                uuid_verificateur=user_uuid,
                date_verification__isnull=False,
            ).count()

            if hasattr(BosquetBaseline, 'uuid_operateur'):
                dashboard['my_bosquets_count'] = BosquetBaseline.objects.filter(
                    uuid_operateur=user_uuid
                ).count()
            if hasattr(Membre, 'uuid_operateur'):
                dashboard['my_membres_count'] = Membre.objects.filter(
                    uuid_operateur=user_uuid
                ).count()
    except Exception:
        pass

    account_fields = [
        ('Email', getattr(user, 'email', '')),
        ('Nom complet', full_name or getattr(user, 'email', '')),
        ('Nom', getattr(user, 'nom', '')),
        ('Prenom', getattr(user, 'prenom', '')),
        ('Telephone', getattr(user, 'num_tel', '')),
        ('Operateur ID', getattr(user, 'operateur_id', '')),
        ('Commune', commune_name),
        ('Adresse', getattr(user, 'adresse', '')),
        ('Genre', getattr(user, 'genre', '')),
        ('Annee de naissance', getattr(user, 'annee_naissance', '')),
        ('UUID utilisateur', user_uuid),
        ('Inscrit le', getattr(user, 'date_joined', None)),
        ('Derniere connexion', getattr(user, 'last_login', None)),
    ]

    status_cards = [
        {
            'label': 'Compte',
            'value': 'Actif' if getattr(user, 'is_active', False) else 'Inactif',
            'state': 'good' if getattr(user, 'is_active', False) else 'danger',
        },
        {
            'label': 'Role application',
            'value': user_role or 'Non defini',
            'state': 'good' if user_role else 'warning',
        },
        {
            'label': 'Role PostgREST',
            'value': postgres_role_code or 'Non assigne',
            'state': 'good' if postgres_role_code else 'warning',
        },
        {
            'label': 'Acces admin',
            'value': 'Superuser' if getattr(user, 'is_superuser', False) else ('Staff' if getattr(user, 'is_staff', False) else 'Utilisateur'),
            'state': 'good' if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) else 'neutral',
        },
    ]

    todo_list = [
        {
            'label': 'Verifier les informations de contact',
            'status': 'done' if getattr(user, 'email', '') and getattr(user, 'num_tel', '') else 'todo',
        },
        {
            'label': 'Completer le rattachement commune',
            'status': 'done' if commune_name else 'todo',
        },
        {
            'label': 'Traiter les PG en attente de verification',
            'status': 'done' if dashboard['my_pending_pg_count'] == 0 else 'todo',
        },
    ]

    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        todo_list.append({
            'label': 'Controler les roles et permissions RBAC',
            'status': 'done' if postgres_role_code else 'todo',
        })

    context = {
        'title': 'Dashboard profil',
        'user_email': getattr(user, 'email', ''),
        'user_name': getattr(user, 'nom', '') or getattr(user, 'username', ''),
        'user_first_name': getattr(user, 'prenom', ''),
        'user_full_name': full_name,
        'user_role': user_role,
        'user_phone': getattr(user, 'num_tel', ''),
        'user_commune': commune_name,
        'postgres_role_code': postgres_role_code,
        'postgres_role_description': postgres_role_description,
        'is_staff': getattr(user, 'is_staff', False),
        'is_superuser': getattr(user, 'is_superuser', False),
        'last_login': getattr(user, 'last_login', None),
        'date_joined': getattr(user, 'date_joined', None),
        'dashboard': dashboard,
        'account_fields': account_fields,
        'status_cards': status_cards,
        'todo_list': todo_list,
    }
    return render(request, 'profile.html', context)


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Déconnecte l'utilisateur depuis les pages publiques ou l'admin.
    """
    logout(request)
    return redirect('home')


# ============================================================================
# LOGIN & AUTHENTICATION
# ============================================================================

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import PostgrestTokenSerializer


class LoginForPostgrestView(TokenObtainPairView):
    serializer_class = PostgrestTokenSerializer

    def post(self, request, *args, **kwargs):
        normalized_data = self.normalize_login_payload(request.data)
        try:
            serializer = self.get_serializer(data=normalized_data)
            serializer.is_valid(raise_exception=True)
            from rest_framework import status
            from rest_framework.response import Response
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as exc:
            if not self.is_missing_auth_user_error(exc):
                raise

        return self.login_with_imported_users_table(normalized_data)

    def normalize_login_payload(self, data):
        normalized = data.copy()
        login_value = (
            normalized.get('email') or
            normalized.get('username') or
            normalized.get('login') or
            normalized.get('user')
        )

        if login_value:
            normalized['email'] = login_value
            normalized['username'] = login_value

        return normalized

    def is_missing_auth_user_error(self, exc):
        current = exc
        while current:
            if 'auth_user' in str(current) and 'does not exist' in str(current):
                return True
            current = getattr(current, '__cause__', None)
        return False

    def login_with_imported_users_table(self, data):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.hashers import check_password
        from django.db.models import Q
        from rest_framework import status
        from rest_framework.response import Response
        from rest_framework_simplejwt.tokens import RefreshToken
        Users = get_user_model()

        username = data.get('username') or data.get('email') or data.get('login') or data.get('user')
        password = data.get('password')
        if not username or not password:
            return Response(
                {'detail': 'email/username et password sont requis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = Users.objects.filter(
            Q(email__iexact=username) |
            Q(operateur_id__iexact=username) |
            Q(nom__iexact=username)
        ).first()

        if not user or not user.is_active or not self.password_matches(password, user.password, check_password):
            return Response(
                {'detail': 'Aucun compte actif ne correspond aux identifiants fournis.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        from core.models_rbac import VALIDATOR_ROLES

        role = user.role or 'Expansion_L1'
        refresh = RefreshToken()
        refresh['role'] = role
        refresh['user_id'] = str(user.uuid_user)
        refresh['username'] = user.email
        refresh['is_validator'] = role in VALIDATOR_ROLES or role == 'postgres'

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    def password_matches(self, raw_password, stored_password, check_password):
        if not stored_password:
            return False
        if check_password(raw_password, stored_password):
            return True
        return raw_password == stored_password


from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from  django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests 
@method_decorator(csrf_exempt, name='dispatch')
class PostgrestProxyView(View):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    @property
    def upstream(self):
        """Dynamically build upstream URL from settings to always use the correct port."""
        try:
            # If POSTGREST_UPSTREAM is explicitly set, use it as-is
            _upstream = getattr(settings, 'POSTGREST_UPSTREAM', None)
            if _upstream:
                return _upstream
            # Otherwise build from host (default 0.0.0.0 for Windows compatibility) and POSTGREST_PORT
            port = getattr(settings, 'POSTGREST_PORT', 3000)
            return f"http://0.0.0.0:{port}"
        except Exception:
            return 'http://0.0.0.0:3000'

    def dispatch(self, request, *args, **kwargs):
        # On tente l'authentification via JWT si l'utilisateur n'est pas déjà authentifié par session
        if not request.user.is_authenticated:
            try:
                auth_header = JWTStatelessUserAuthentication().authenticate(request)
                if auth_header:
                    request.user, _ = auth_header
            except Exception:
                pass

        # Vérification manuelle de l'authentification car ProxyView n'est pas une APIView de DRF
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentification requise."}, status=401)

        return self.forward_to_postgrest(request, kwargs.get('path', ''))

    def forward_to_postgrest(self, request, path):
        target_url = self.build_upstream_url(path, request.GET)
        body = request.body if request.method in {'POST', 'PUT', 'PATCH'} else None
        proxy_request = Request(
            target_url,
            data=body,
            headers=self.build_upstream_headers(request),
            method=request.method,
        )

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔗 PostgREST Proxy: {request.method} {target_url}")
        logger.info(f"   Upstream: {self.upstream}")

        try:
            with urlopen(proxy_request, timeout=30) as upstream_response:
                return self.build_django_response(
                    upstream_response.read(),
                    upstream_response.status,
                    upstream_response.headers,
                )
        except HTTPError as exc:
            logger.error(f"❌ PostgREST HTTP Error {exc.code}: {exc.read().decode()}")
            return self.build_django_response(
                exc.read(),
                exc.code,
                exc.headers,
            )
        except URLError as exc:
            logger.error(f"❌ PostgREST URLError: {exc.reason}")
            return JsonResponse(
                {
                    "detail": "PostgREST est inaccessible.",
                    "error": str(exc.reason),
                    "upstream": self.upstream,
                },
                status=502,
            )
        except Exception as exc:
            logger.error(f"❌ Erreur proxy PostgREST: {type(exc).__name__}: {exc}")
            import traceback
            logger.error(traceback.format_exc())
            return JsonResponse(
                {
                    "detail": "Erreur lors du proxy PostgREST.",
                    "error": str(exc),
                    "upstream": self.upstream,
                },
                status=502,
            )

    def build_upstream_url(self, path, query_params):
        clean_path = path.lstrip('/')
        target_url = f"{self.upstream.rstrip('/')}/{clean_path}"
        query_string = query_params.urlencode()
        if query_string:
            target_url = f"{target_url}?{query_string}"
        return target_url

    def build_upstream_headers(self, request):
        allowed_headers = {
            'accept',
            'authorization',
            'content-type',
            'prefer',
            'range',
            'range-unit',
        }
        headers = {}
        for header_name, header_value in request.headers.items():
            if header_name.lower() in allowed_headers:
                headers[header_name] = header_value
        return headers

    def build_django_response(self, content, status_code, upstream_headers):
        response = HttpResponse(content, status=status_code)
        excluded_headers = {
            'connection',
            'content-encoding',
            'content-length',
            'keep-alive',
            'proxy-authenticate',
            'proxy-authorization',
            'te',
            'trailer',
            'transfer-encoding',
            'upgrade',
        }
        for header_name, header_value in upstream_headers.items():
            if header_name.lower() not in excluded_headers:
                response[header_name] = header_value
        return response
    def post(self, request, *args, **kwargs): 
        endpoint = request.path.split('/api/')[-1]
        postgrest_url = f"{self.upstream.rstrip('/')}/{endpoint}"
        # Récupération sécurisée du token d'autorisation original 
        headers = { 
                   'Authorization': request.headers.get('Authorization'),
                   'Content-Type': 'application/json', 
                   # Force PostgREST à ignorer le dictionnaire 'fid' s'il n'existe pas en BDD 
                   # et à utiliser la vraie clé primaire de la table pour l'upsert 
                   'Prefer': 'resolution=merge' } 
        try: 
            # Extraction propre du JSON envoyé par QGIS 
            if request.body: 
                json_data = json.loads(request.body.decode('utf-8')) 
            else: json_data = {} 
        except json.JSONDecodeError: 
            return JsonResponse({'error': 'JSON invalide reçu par le proxy'}, status=400) 
        # Transmission propre du flux JSON à PostgREST 
        response = requests.post(postgrest_url, json=json_data, headers=headers) 
        try: 
            return JsonResponse(response.json(), status=response.status_code, safe=False) 
        except Exception: 
            return JsonResponse({'message': response.text}, status=response.status_code)


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
            'user__email',
            'content_type__model',
            'action_flag',
            'action_time'
        ).order_by('-action_time')[:100]
        
        action_names = {1: 'CREATE', 2: 'EDIT', 3: 'DELETE'}
        
        logs_list = []
        for log in logs:
            logs_list.append({
                'username': log['user__email'],
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
