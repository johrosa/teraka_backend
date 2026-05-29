from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models_rbac import DEFAULT_POSTGRES_ROLE_CODES


class PostgrestTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Récupérer le rôle depuis les groupes Django
        rbac_groups = DEFAULT_POSTGRES_ROLE_CODES

        user_groups = user.groups.filter(name__in=rbac_groups).values_list('name', flat=True)

        if user_groups:
            # Prendre le premier groupe trouvé (normalement un seul)
            role = user_groups[0]
        else:
            # Rôle par défaut si pas de groupe RBAC
            role = 'postgres' if user.is_superuser else 'Expansion_L1'

        # Claims pour PostgREST
        token['role'] = role
        token['user_id'] = str(user.pk)
        token['username'] = user.username
        token['is_validator'] = user.is_staff

        return token
