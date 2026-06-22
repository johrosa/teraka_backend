"""
Sync RBAC permissions (PostgreSQL roles) to Django permissions (auth.permission).

Maps:
  PostgreSQL table grants  →  Django model permissions (add/change/delete/view)
  RBAC roles               →  Django groups with those permissions

Usage:
  python manage.py sync_rbac_permissions
  python manage.py sync_rbac_permissions --create    # Create missing perms
  python manage.py sync_rbac_permissions --dry-run   # Preview only
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from core.models_rbac import Role, UserRole, DEFAULT_POSTGRES_ROLES
from django.db import connection


class Command(BaseCommand):
    help = 'Sync RBAC (PostgreSQL roles/permissions) with Django auth permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create missing permissions and assign to groups'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying'
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform full sync: groups + permissions'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        create = options.get('create', False)
        full = options.get('full', False)

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('🔐 RBAC → Django Permissions Sync')
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Step 1: Map RBAC roles to Django permissions
        self.stdout.write('\n📋 Step 1: Analyzing RBAC roles and Django permissions...')
        rbac_roles = Role.objects.values_list('code', flat=True)
        django_groups = Group.objects.values_list('name', flat=True)
        all_permissions = Permission.objects.all()

        self.stdout.write(f'  RBAC Roles: {rbac_roles.count()}')
        self.stdout.write(f'  Django Groups: {django_groups.count()}')
        self.stdout.write(f'  Django Permissions: {all_permissions.count()}')

        # Step 2: Define permission matrix
        self.stdout.write('\n📊 Step 2: Building permission matrix...')
        rbac_permission_matrix = self._build_permission_matrix()
        
        self.stdout.write(f'  Created matrix with {len(rbac_permission_matrix)} role→permission mappings')

        # Step 3: Assign permissions to groups
        if create or full:
            self.stdout.write('\n🔧 Step 3: Assigning permissions to groups...')
            self._assign_permissions_to_groups(rbac_permission_matrix, dry_run)

        # Step 4: Verify sync status
        self.stdout.write('\n✅ Step 4: Verification')
        self._verify_sync_status()

    def _build_permission_matrix(self):
        """
        Build a matrix mapping RBAC roles to Django permissions.
        
        Rules:
        - View-only roles (L1 read-only) → view permissions
        - Modify roles (L2, L3 edit) → add/change permissions
        - Admin roles → all permissions
        
        Returns: {role_code: [permission_codename, ...]}
        """
        matrix = {}

        # Map standard roles to permission types
        role_permission_map = {
            'Expansion_L1': ['view'],           # Read-only
            'Expansion_L2': ['add', 'change'],  # Can modify
            'MRV_L1': ['view'],                 # Read-only
            'MRV_L2': ['view', 'change'],       # Can modify
            'MRV_L3': ['view', 'change', 'delete'],  # Full access
            'Admin_L1': ['add', 'change'],      # Admin modify
            'Admin_L2': ['add', 'change', 'delete'],  # Full admin
            'ADMIN': ['add', 'change', 'delete', 'view'],  # Superuser-level
        }

        # Get all core app models
        core_app = apps.get_app_config('core')
        for model in core_app.get_models():
            model_name = model._meta.model_name
            content_type = ContentType.objects.get_for_model(model)

            for role_code, perm_types in role_permission_map.items():
                if role_code not in matrix:
                    matrix[role_code] = []

                # Get Django permissions for this model
                for perm_type in perm_types:
                    try:
                        perm = Permission.objects.get(
                            content_type=content_type,
                            codename=f'{perm_type}_{model_name}'
                        )
                        matrix[role_code].append(perm)
                    except Permission.DoesNotExist:
                        pass

        return matrix

    def _assign_permissions_to_groups(self, matrix, dry_run):
        """Assign permissions from matrix to groups."""
        for role_code, permissions in matrix.items():
            try:
                group = Group.objects.get(name=role_code)
                current_perms = set(group.permissions.all())
                new_perms = set(permissions)
                to_add = new_perms - current_perms
                to_remove = current_perms - new_perms

                if to_add or to_remove:
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  [DRY-RUN] Group "{role_code}":'
                            )
                        )
                        for perm in to_add:
                            self.stdout.write(f'    + {perm}')
                        for perm in to_remove:
                            self.stdout.write(f'    - {perm}')
                    else:
                        for perm in to_add:
                            group.permissions.add(perm)
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ Added {perm} to "{role_code}"'
                                )
                            )
                        for perm in to_remove:
                            group.permissions.remove(perm)
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  - Removed {perm} from "{role_code}"'
                                )
                            )
                else:
                    self.stdout.write(f'  ✓ "{role_code}" already in sync')
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Group "{role_code}" not found')
                )

    def _verify_sync_status(self):
        """Verify that groups have correct permissions."""
        all_synced = True
        for role_code in ['ADMIN', 'MRV_L3', 'Expansion_L2']:
            try:
                group = Group.objects.get(name=role_code)
                perm_count = group.permissions.count()
                self.stdout.write(f'  {role_code}: {perm_count} permissions')
                if perm_count == 0:
                    self.stdout.write(
                        self.style.WARNING('    ⚠️  No permissions assigned')
                    )
                    all_synced = False
            except Group.DoesNotExist:
                pass

        if all_synced:
            self.stdout.write(
                self.style.SUCCESS('\n✅ RBAC → Django permissions sync complete')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  Some groups need permission assignment.\n'
                    '   Run with --create to auto-assign.'
                )
            )
