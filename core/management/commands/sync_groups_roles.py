"""
Management command to sync Django Groups with PostgreSQL roles.
Use this to ensure auth.Group entries automatically create/update DB roles.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models_rbac import Role, DEFAULT_POSTGRES_ROLES
from django.db import connection


class Command(BaseCommand):
    help = 'Sync Django auth.Group with PostgreSQL roles (Role model)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create Groups for all roles if they don\'t exist'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        create = options.get('create', False)

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('🔄 Django Groups ↔ PostgreSQL Roles Sync')
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Step 1: Get all current roles from DB
        db_roles = set(Role.objects.values_list('code', flat=True))
        self.stdout.write(f"\n📊 Database roles: {len(db_roles)}")
        for role in sorted(db_roles):
            self.stdout.write(f"  • {role}")

        # Step 2: Get all Django Groups
        groups = set(Group.objects.values_list('name', flat=True))
        self.stdout.write(f"\n👥 Django Groups: {len(groups)}")
        for group in sorted(groups):
            self.stdout.write(f"  • {group}")

        # Step 3: Find mismatches
        missing_groups = db_roles - groups
        missing_roles = groups - db_roles

        if missing_groups:
            self.stdout.write(
                self.style.WARNING(f"\n⚠️  Missing Django Groups (exist in DB but not in auth.Group):")
            )
            for group in sorted(missing_groups):
                self.stdout.write(f"  • {group}")

        if missing_roles:
            self.stdout.write(
                self.style.WARNING(f"\n⚠️  Missing DB Roles (exist in Groups but not in Role model):")
            )
            for role in sorted(missing_roles):
                self.stdout.write(f"  • {role}")

        # Step 4: Sync if requested
        if create:
            self.stdout.write(self.style.SUCCESS('\n✨ Creating missing Groups...'))
            created = 0
            for role_code in missing_groups:
                if not dry_run:
                    Group.objects.get_or_create(name=role_code)
                    self.stdout.write(f"  ✓ Created Group: {role_code}")
                    created += 1
                else:
                    self.stdout.write(f"  [DRY-RUN] Would create Group: {role_code}")

            if dry_run:
                self.stdout.write(self.style.WARNING(f'\n[DRY-RUN] Would create {len(missing_groups)} groups'))
            else:
                self.stdout.write(self.style.SUCCESS(f'\n✅ Created {created} groups'))

        # Step 5: Show final state
        final_groups = set(Group.objects.values_list('name', flat=True))
        final_roles = set(Role.objects.values_list('code', flat=True))

        if final_groups == final_roles:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ SYNC COMPLETE: {len(final_groups)} Groups ↔ {len(final_roles)} Roles'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  Still out of sync: {len(final_groups)} Groups vs {len(final_roles)} Roles'
                )
            )
