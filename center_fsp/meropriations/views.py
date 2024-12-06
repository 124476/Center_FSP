from django.views.generic.edit import FormView
import django.views.generic

from users.models import User
from meropriations.models import Meropriation


class MeropriationList(django.views.generic.ListView):
    template_name = "meropriations/list_meropriation.html"
    context_object_name = "meropriations"

    def get_queryset(self):
        region = self.request.GET.get("region")
        if region:
            return Meropriation.objects.filter(region=region)
        return Meropriation.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Мероприятия"
        return context


__all__ = ()
