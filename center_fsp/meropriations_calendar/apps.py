__all__ = ()
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MeropriationsCalendarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "meropriations_calendar"
    verbose_name = _("meropriations_calendar")
