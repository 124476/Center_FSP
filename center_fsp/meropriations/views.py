from django.http import Http404
from django.views.generic.edit import FormView
import django.views.generic

from meropriations.models import Meropriation


class MeropriationList(django.views.generic.ListView):
    template_name = "meropriations/list_meropriation.html"
    context_object_name = "meropriations"

    def get_queryset(self):
        region = self.request.user.region
        if not region:
            raise Http404("Регион не указан.")
        queryset = Meropriation.objects.filter(region=region)
        if not queryset.exists():
            raise Http404("Мероприятия для указанного региона не найдены.")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Мероприятия"
        return context


__all__ = ()
