from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PostgrestTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # On récupère le rôle PostgreSQL associé à l'utilisateur
        try:
            from core.models_rbac import UserRole
            user_role = UserRole.objects.select_related('role').get(user=user)
            role = user_role.role.code
        except UserRole.DoesNotExist:
            # Si l'utilisateur n'a pas de rôle assigné, utiliser un rôle par défaut
            # 'postgres' = superuser (utile pour les admins)
            # ou utiliser 'Expansion_L1' pour les utilisateurs standard
            role = 'postgres' if user.is_superuser else 'Expansion_L1'
        except Exception as e:
            # En cas d'erreur, utiliser postgres comme fallback
            role = 'postgres'
        
        # On définit les "claims" pour PostgREST
        token['role'] = role
        token['user_id'] = str(user.pk)
        token['username'] = user.username
        try:
            from core.models_rbac import VALIDATOR_ROLES
            is_validator = role in VALIDATOR_ROLES or role == 'postgres'
        except Exception:
            is_validator = user.is_staff

        token['is_validator'] = is_validator

        return token
