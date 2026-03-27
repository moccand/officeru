from django.apps import AppConfig


class BackofficeConfig(AppConfig):
    name = 'backoffice'

    def ready(self):
        # Ensure model save signals are registered at startup.
        from . import signals  # noqa: F401
