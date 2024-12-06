from django.apps import AppConfig


class MeropriationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "meropriations"

    def ready(self):
        import meropriations.signals
