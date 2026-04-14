from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PostgrestTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # On définit les "claims" pour PostgREST
        # Utilisons un rôle standard ou celui de l'utilisateur.
        # Pour le test, on met 'postgres' qui est le superuser défini dans settings.py
        token['role'] = 'postgres'
        token['user_id'] = user.id
        # On récupère un droit de validation (ex: si l'user est staff)
        token['is_validator'] = user.is_staff

        return token