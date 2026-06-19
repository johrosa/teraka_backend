"""
Signals to sync Django Groups with PostgreSQL roles automatically.
Connect these in apps.py ready() method.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from core.models_rbac import Role


@receiver(post_save, sender=Group)
def sync_group_to_role_on_save(sender, instance, created, **kwargs):
    """
    When a Django Group is created or updated, ensure corresponding Role exists in DB.
    """
    if created:
        # Check if Role already exists
        role, created_role = Role.objects.get_or_create(
            code=instance.name,
            defaults={'description': f'Synced from Django Group: {instance.name}'}
        )
        if created_role:
            print(f'✓ Created Role "{instance.name}" (synced from Group)')
    else:
        # Update existing Role description if Group changed
        try:
            role = Role.objects.get(code=instance.name)
            if not role.description:
                role.description = f'Django Group: {instance.name}'
                role.save()
        except Role.DoesNotExist:
            pass


@receiver(post_delete, sender=Group)
def sync_group_to_role_on_delete(sender, instance, **kwargs):
    """
    When a Django Group is deleted, optionally delete corresponding Role.
    WARNING: Disabled by default to prevent accidental cascades.
    Uncomment if you want automatic cleanup.
    """
    # try:
    #     role = Role.objects.get(code=instance.name)
    #     role.delete()
    #     print(f'✓ Deleted Role "{instance.name}" (synced from Group deletion)')
    # except Role.DoesNotExist:
    #     pass
    pass


@receiver(post_save, sender=Role)
def sync_role_to_group_on_save(sender, instance, created, **kwargs):
    """
    When a Role is created or updated, ensure corresponding Group exists in Django.
    """
    if created:
        # Check if Group already exists
        group, created_group = Group.objects.get_or_create(name=instance.code)
        if created_group:
            print(f'✓ Created Group "{instance.code}" (synced from Role)')
    else:
        # Ensure Group exists with same name
        group, _ = Group.objects.get_or_create(name=instance.code)
