from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import FormView, CreateView
import django.views.generic

from meropriations.models import Meropriation
from meropriations.forms import MeropriationForm


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


class MeropriationCreateView(CreateView):
    model = Meropriation
    form_class = MeropriationForm
    template_name = "meropriations/meropriation_form.html"
    success_url = reverse_lazy("meropriations:meropriations")

    def form_valid(self, form):
        form.instance.region = self.request.user.region
        form.instance.status = Meropriation.Status.CONSIDERATION
        return super().form_valid(form)


class MeropriationDetailView(DetailView):
    model = Meropriation
    template_name = "meropriations/meropriation_detail.html"
    context_object_name = "meropriation"


__all__ = ()
