"""
Management command pour assigner des rôles PostgreSQL aux utilisateurs Django
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from core.models_rbac import Role, UserRole


class Command(BaseCommand):
    help = 'Assigne un rôle PostgreSQL à un utilisateur Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nom d\'utilisateur Django',
        )
        parser.add_argument(
            '--role',
            type=str,
            help='Rôle PostgreSQL à assigner',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Lister tous les utilisateurs et leurs rôles',
        )
        parser.add_argument(
            '--list-roles',
            action='store_true',
            help='Lister tous les rôles disponibles',
        )

    def handle(self, *args, **options):
        # Lister les rôles disponibles
        if options['list_roles']:
            self.stdout.write(self.style.SUCCESS('Rôles PostgreSQL disponibles:'))
            self.stdout.write('')
            if not Role.objects.exists():
                Role.ensure_default_roles()

            for role in Role.objects.all():
                self.stdout.write(f"  • {role.code:<20} - {role.description}")
            self.stdout.write('')
            return

        # Lister les associations actuelles
        if options['list']:
            self.stdout.write(self.style.SUCCESS('Associations Utilisateur-Rôle:'))
            self.stdout.write('')
            
            user_roles = UserRole.objects.select_related('user').all()
            
            if not user_roles.exists():
                self.stdout.write('  Aucune association trouvée.')
            else:
                self.stdout.write(f"  {'Utilisateur':<20} {'Rôle':<20} {'Depuis':<20}")
                self.stdout.write('  ' + '-' * 60)
                
                for ur in user_roles:
                    self.stdout.write(
                        f"  {ur.user.username:<20} {ur.role:<20} {ur.created_at.strftime('%Y-%m-%d %H:%M'):<20}"
                    )
            
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'Total: {user_roles.count()} association(s)'))
            
            # Lister aussi les utilisateurs sans rôle
            users_without_role = User.objects.exclude(
                pk__in=UserRole.objects.values_list('user_id', flat=True)
            )
            
            if users_without_role.exists():
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('Utilisateurs sans rôle assigné:'))
                self.stdout.write('')
                
                for user in users_without_role:
                    self.stdout.write(f"  • {user.username} ({user.email})")
            
            return

        # Assigner un rôle
        if options['username'] and options['role']:
            try:
                user = User.objects.get(username=options['username'])
            except User.DoesNotExist:
                raise CommandError(f"L'utilisateur '{options['username']}' n'existe pas.")

            if not Role.objects.exists():
                Role.ensure_default_roles()

            try:
                role_obj = Role.objects.get(code=options['role'])
            except Role.DoesNotExist:
                raise CommandError(f"Le rôle '{options['role']}' n'existe pas. Utilisez --list-roles pour voir les rôles disponibles.")

            try:
                user_role = UserRole.objects.get(user=user)
                old_role = user_role.role.code
                user_role.role = role_obj
                user_role.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Le rôle de '{user.username}' a été mis à jour: {old_role} → {role_obj.code}"
                    )
                )
            except UserRole.DoesNotExist:
                user_role = UserRole.objects.create(user=user, role=role_obj)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"L'utilisateur '{user.username}' a été associé au rôle '{role_obj.code}'"
                    )
                )

            return

        # Si aucune option n'est fournie
        self.stdout.write(self.style.WARNING('Utilisation:'))
        self.stdout.write('  python manage.py assign_user_role --username <username> --role <role>')
        self.stdout.write('  python manage.py assign_user_role --list')
        self.stdout.write('  python manage.py assign_user_role --list-roles')
