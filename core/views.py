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