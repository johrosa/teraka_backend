from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PostgrestTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # On récupère le rôle PostgreSQL associé à l'utilisateur
        try:
            from core.models_rbac import UserRole
            user_role = UserRole.objects.get(user=user)
            role = user_role.role
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
        token['user_id'] = user.id
        token['username'] = user.username
        # On récupère un droit de validation (ex: si l'user est staff)
        token['is_validator'] = user.is_staff

        return token