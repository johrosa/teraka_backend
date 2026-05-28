from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PostgrestTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # On authentifie l'utilisateur d'abord
        # On utilise le validate du grand-parent (TokenObtainSerializer)
        # pour éviter que TokenObtainPairSerializer n'appelle get_token trop tôt
        from rest_framework_simplejwt.serializers import TokenObtainSerializer
        data = TokenObtainSerializer.validate(self, attrs)

        # On récupère le rôle demandé et on l'attache à l'objet user
        # pour qu'il soit accessible dans la méthode de classe get_token
        requested_role = self.context['request'].data.get('role')
        if requested_role:
            self.user._requested_role = requested_role

        # Maintenant on génère le token (ce qui appelle get_token)
        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # On récupère le rôle PostgreSQL associé à l'utilisateur
        try:
            from core.models_rbac import UserRole, Role
            user_role = UserRole.objects.select_related('role').get(user=user)
            assigned_role = user_role.role

            # Logique de sélection de rôle (Principe du moindre privilège)
            requested_code = getattr(user, '_requested_role', None)

            if requested_code:
                # Si un rôle est demandé, on vérifie s'il est autorisé (même catégorie, niveau inférieur ou égal)
                try:
                    requested_obj = Role.objects.get(code=requested_code)
                    if (requested_obj.get_category() == assigned_role.get_category() and
                        requested_obj.level <= assigned_role.level):
                        final_role = requested_obj
                    else:
                        # Rôle demandé non autorisé, on bascule sur le plus bas par défaut
                        final_role = Role.get_lowest_for_category(assigned_role.get_category()) or assigned_role
                except Role.DoesNotExist:
                    final_role = Role.get_lowest_for_category(assigned_role.get_category()) or assigned_role
            else:
                # Pas de rôle demandé -> On prend le niveau 1 par défaut (Sécurité)
                final_role = Role.get_lowest_for_category(assigned_role.get_category()) or assigned_role

            role = final_role.code
            level = final_role.level

        except UserRole.DoesNotExist:
            # Si l'utilisateur n'a pas de rôle assigné, utiliser un rôle par défaut restreint
            role = 'postgres' if user.is_superuser else 'Expansion_L1'
            level = 3 if user.is_superuser else 1
        except Exception as e:
            role = 'postgres'
            level = 3
        
        # On définit les "claims" pour PostgREST
        token['role'] = role
        token['level'] = level
        token['user_id'] = str(user.pk)
        token['username'] = user.email
        # On récupère un droit de validation (ex: si l'user est staff)
        token['is_validator'] = user.is_staff

        return token
