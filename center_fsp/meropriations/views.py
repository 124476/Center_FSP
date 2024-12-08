import csv

from allauth.core.internal.httpkit import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import django.shortcuts
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
import django.views.generic
import django.forms

from meropriations.models import Meropriation, Result, Notification, Team
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


class MeropriationCreateView(LoginRequiredMixin, CreateView):
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


class MeropriationDetailView(LoginRequiredMixin, DetailView):
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
        last_status = meropriation.status
        url = django.urls.reverse('meropriations:meropriation_detail',
                                  kwargs={'pk': meropriation.pk})

        if not request.user.is_superuser:
            messages.error(request,
                           "Вы не имеете прав на выполнение этого действия")
            return redirect(url)

        form = MeropriationStatusForm(request.POST, instance=meropriation)
        if form.is_valid():
            form.save()
            Notification.objects.create(
                meropriation=meropriation,
                text=f"Статус изменен с '{last_status}' на '{meropriation.status}'",
            )
            messages.success(request, "Статус успешно обновлен!")
            return redirect(url)
        else:
            messages.error(request, "Ошибка при обновлении статуса.")
        return redirect(url)


class ResultCreateView(LoginRequiredMixin, CreateView):
    template_name = "meropriations/new_results.html"

    def get(self, request):
        user_region = self.request.user.region
        if not user_region:
            return redirect('meropriations:meropriations')

        meropriations = Meropriation.objects.filter(region=user_region,
                                                    status='Принят')

        return django.shortcuts.render(request,
                                       "meropriations/new_results.html",
                                       {
                                           "meropriations": meropriations,
                                           "title": "Загрузка",
                                       })

    def post(self, request):
        user_region = self.request.user.region
        if not user_region:
            return redirect('meropriations:meropriations')

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
                if files[i].name.endswith('.xlsx') or files[i].name.endswith(
                        '.xls'):
                    parse_excel_file(files[i],
                                     form.cleaned_data['meropriation'].id)
                elif files[i].name.endswith('.txt') or files[i].name.endswith(
                        '.csv'):
                    parse_txt_file(files[i],
                                   form.cleaned_data['meropriation'].id)
                else:
                    messages.error(request,
                                   "Есть не подходящие типы файлов, посмотрите инструкцию!")
                    user_region = self.request.user.region
                    meropriations = Meropriation.objects.filter(
                        region=user_region,
                        status='Принят')
                    return django.shortcuts.render(request,
                                                   "meropriations/new_results.html",
                                                   {
                                                       "meropriations": meropriations,
                                                       "title": "Загрузка",
                                                   })

        return django.shortcuts.redirect("meropriations:meropriations")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Загрузка"
        return context


class GenerateResultReportView(DetailView):
    def get(self, request, *args, **kwargs):
        meropriation_id = kwargs.get("meropriation_id")

        try:
            meropriation = Meropriation.objects.get(id=meropriation_id)
        except Meropriation.DoesNotExist:
            return HttpResponse(status=404, content="Мероприятие не найдено.")

        all_teams = Team.objects.filter(
            result__meropriation=meropriation).order_by("-status")
        winners = Team.objects.filter(result__meropriation=meropriation,
                                      status="Победитель").count()
        prizers = Team.objects.filter(result__meropriation=meropriation,
                                      status="Призёр").count()
        participants = Team.objects.filter(result__meropriation=meropriation,
                                           status="Участник").count()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="result_report_{meropriation_id}.csv"'

        writer = csv.writer(response)

        writer.writerow(["Статистика", "Количество"])
        writer.writerow(["Победителей", winners])
        writer.writerow(["Призёров", prizers])
        writer.writerow(["Участников", participants])
        writer.writerow(["Общее количество участников", participants + winners + prizers])

        writer.writerow([])

        writer.writerow(["Команда", "Статус"])
        for team in all_teams:
            status = "участник"
            if team.status == "PRIZER":
                status = "призер"
            elif team.status == "WINNER":
                status = "победитель"
            writer.writerow([team.name, status])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Загрузка"
        return context


class Notifications(LoginRequiredMixin, django.views.generic.ListView):
    template_name = "meropriations/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        region = self.request.user.region
        if not region:
            return redirect('homepage:main')
        return Notification.objects.filter(meropriation__region=region)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Уведомления"
        return context


__all__ = ()
