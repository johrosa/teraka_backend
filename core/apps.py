from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # Register signal handlers for Django Groups ↔ PostgreSQL Roles sync
        from core import signals  # noqa
