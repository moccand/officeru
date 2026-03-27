from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # Ensure model save signals are registered at startup.
        from . import signals  # noqa: F401
