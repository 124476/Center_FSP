from allauth.core.internal.httpkit import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import django.shortcuts
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
import django.views.generic
import django.forms

from meropriations.models import Meropriation, Result
from meropriations.forms import MeropriationForm, ResultForm, \
    MeropriationStatusForm
from meropriations.parsers.parser_xlsx import parse_excel_file
from meropriations.parsers.parser_txt import parse_txt_file

class MeropriationList(LoginRequiredMixin, django.views.generic.ListView):
    template_name = "meropriations/list_meropriation.html"
    context_object_name = "meropriations"

    def get_queryset(self):
        region = self.request.user.region
        if self.request.user.is_staff:
            return Meropriation.objects.filter()
        elif not region:
            return Meropriation.objects.none()
        return Meropriation.objects.filter(region=region)

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
        form.instance.normal_place = form.cleaned_data['normal_place']
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            messages.error(request,
                           "Сотрудники не могут создавать мероприятия.")
            return redirect("meropriations:meropriations")
        return super().dispatch(request, *args, **kwargs)


class MeropriationDetailView(DetailView):
    model = Meropriation
    template_name = "meropriations/meropriation_detail.html"
    context_object_name = "meropriation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['status_form'] = MeropriationStatusForm(
                instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        meropriation = self.get_object()
        url = django.urls.reverse('meropriations:meropriation_detail',
                                  kwargs={'pk': meropriation.pk})

        if not request.user.is_superuser:
            messages.error(request,
                           "Вы не имеете прав на выполнение этого действия")
            return redirect(url)

        form = MeropriationStatusForm(request.POST, instance=meropriation)
        if form.is_valid():
            form.save()
            messages.success(request, "Статус успешно обновлен!")
            return redirect(url)
        else:
            messages.error(request, "Ошибка при обновлении статуса.")
        return redirect(url)


class ResultList(django.views.generic.ListView):
    template_name = "meropriations/results.html"
    context_object_name = "results"

    def get_queryset(self):
        region = self.request.user.region
        queryset = Result.objects.all()
        if region:
            queryset = queryset.filter(meropriation__region=region)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Результаты"
        return context


class ResultCreateView(CreateView):
    template_name = "meropriations/new_results.html"

    def get(self, request):
        user_region = self.request.user.region
        meropriations = Meropriation.objects.filter(region=user_region, status='Принят')

        return django.shortcuts.render(request,
                                       "meropriations/new_results.html",
                                       {
                                           "meropriations": meropriations,
                                           "title": "Загрузка",
                                       })

    def post(self, request):
        files_count = int(request.POST.get('files_count', 0))
        files = request.FILES.getlist('file')
        merops = request.POST.getlist('meropriation')

        if len(files) != files_count or len(merops) != files_count:
            messages.error(request, "Заполните все поля")
            user_region = self.request.user.region
            meropriations = Meropriation.objects.filter(region=user_region,
                                                        status='Принят')
            return django.shortcuts.render(request,
                                           "meropriations/new_results.html",
                                           {
                                               "meropriations": meropriations,
                                               "title": "Загрузка",
                                           })

        for i in range(files_count):
            form = ResultForm({
                'file': files[i],
                'meropriation': merops[i]
            })
            if form.is_valid():
                if files[i].name.endswith('.xlsx') or files[i].name.endswith('.xls'):
                    parse_excel_file(files[i], form.cleaned_data['meropriation'].id)
                elif files[i].name.endswith('.txt') or files[i].name.endswith('.csv'):
                    parse_txt_file(files[i], form.cleaned_data['meropriation'].id)
                else:
                    messages.error(request, "Есть не подходящие типы файлов, посмотрите инструкцию!")
                    user_region = self.request.user.region
                    meropriations = Meropriation.objects.filter(region=user_region,
                                                                status='Принят')
                    return django.shortcuts.render(request,
                                                   "meropriations/new_results.html",
                                                   {
                                                       "meropriations": meropriations,
                                                       "title": "Загрузка",
                                                   })

        return django.shortcuts.redirect("meropriations:results")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Загрузка"
        return context


__all__ = ()
