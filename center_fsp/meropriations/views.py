import csv

from allauth.core.internal.httpkit import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import django.shortcuts
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, View
from django.views.generic.edit import CreateView
import django.views.generic
import django.forms

from meropriations.models import Meropriation, Result, Notification, Team, \
    Participant
from meropriations.forms import MeropriationForm, ResultForm
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


class MeropriationCreateView(LoginRequiredMixin, CreateView):
    model = Meropriation
    form_class = MeropriationForm
    template_name = "meropriations/meropriation_form.html"
    success_url = reverse_lazy("meropriations:meropriations")

    def form_valid(self, form):
        form.instance.region = self.request.user.region
        return super().form_valid(form)


class MeropriationDetailView(LoginRequiredMixin, DetailView):
    model = Meropriation
    template_name = "meropriations/meropriation_detail.html"
    context_object_name = "meropriation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        meropriation = self.get_object()

        last_status = "Не опубликован"
        if meropriation.is_published:
            last_status = "Опубликован"

        url = django.urls.reverse('meropriations:meropriation_detail',
                                  kwargs={'pk': meropriation.pk})

        if not request.user.is_superuser:
            messages.error(request,
                           "Вы не имеете прав на выполнение этого действия")
            return django.shortcuts.redirect(url)

        now_status = "Не опубликован"
        if not meropriation.is_published:
            now_status = "Опубликован"
            meropriation.is_published = True
        else:
            meropriation.is_published = False

        meropriation.save()
        Notification.objects.create(
            meropriation=meropriation,
            text=f"Статус изменен с '{last_status}' на '{now_status}'",
        )
        messages.success(request, "Статус успешно обновлен!")
        return django.shortcuts.redirect(url)


class ResultCreateView(LoginRequiredMixin, CreateView):
    template_name = "meropriations/new_results.html"

    def get(self, request):
        user_region = self.request.user.region
        if not user_region:
            return django.shortcuts.redirect('meropriations:meropriations')

        meropriations = Meropriation.objects.filter(region=user_region, is_published=True)

        return django.shortcuts.render(request,
                                       "meropriations/new_results.html",
                                       {
                                           "meropriations": meropriations,
                                           "title": "Загрузка",
                                       })

    def post(self, request):
        user_region = self.request.user.region
        if not user_region:
            return django.shortcuts.redirect('meropriations:meropriations')

        meropriations = Meropriation.objects.filter(region=user_region, is_published=True)

        meropriation_id = request.POST.get('meropriation')
        try:
            meropriation = Meropriation.objects.get(id=meropriation_id)
        except Meropriation.DoesNotExist:
            messages.error(request, "Выбранное мероприятие некорректно.")
            return django.shortcuts.redirect('meropriations:results_new')

        files = request.FILES.getlist('file')
        if not files:
            messages.error(request, "Вы не загрузили файлы.")
            return django.shortcuts.redirect('meropriations:results_new')

        teams = Team.objects.filter(result__meropriation_id=meropriation_id)
        for team in teams:
            team.delete()
        Result.objects.filter(meropriation_id=meropriation_id).delete()

        for uploaded_file in files:
            if uploaded_file.name.endswith(
                    '.xlsx') or uploaded_file.name.endswith('.xls'):
                parse_excel_file(uploaded_file, meropriation.id)
            elif uploaded_file.name.endswith(
                    '.txt') or uploaded_file.name.endswith('.csv'):
                parse_txt_file(uploaded_file, meropriation.id)
            else:
                messages.error(request,
                               "Неподдерживаемый тип файла: {}".format(
                                   uploaded_file.name))
                return django.shortcuts.redirect('meropriations:results_new')

        results = Result.objects.filter(meropriation=meropriation).all()

        if not results:
            messages.error(request, "Нет результатов")
            return django.shortcuts.redirect('meropriations:results_new')

        teams = [result.team for result in results if result.team]

        participants = Participant.objects.filter(team__in=teams).distinct()

        messages.success(request, "Файлы успешно загружены и обработаны.")
        return django.shortcuts.render(request,
                                       "meropriations/new_results.html",
                                       {
                                           "uploaded": True,
                                           "meropriations": meropriations,
                                           "participants": participants,
                                           "title": "Загрузка",
                                       })


class AddTeamView(View):
    def post(self, request):
        meropriation_id = request.POST.get('meropriation')
        team_name = request.POST.get('team_name')

        if not meropriation_id or not team_name:
            messages.error(request,
                           "Ошибка: все поля обязательны для заполнения.")
            return django.shortcuts.redirect('meropriations:add_team')

        try:
            meropriation = Meropriation.objects.get(id=meropriation_id)
        except Meropriation.DoesNotExist:
            messages.error(request, "Выбранное мероприятие некорректно.")
            return django.shortcuts.redirect('meropriations:add_team')

        Team.objects.create(name=team_name)

        messages.success(request,
                         f"Команда '{team_name}' успешно добавлена на мероприятие '{meropriation.name}'")
        return django.shortcuts.redirect('meropriations:results_new')


class DeleteParticipantView(View):
    def post(self, request, participant_id):
        try:
            participant = Participant.objects.get(id=participant_id)
            participant.delete()
            messages.success(request, "Участник успешно удален.")
        except Participant.DoesNotExist:
            messages.error(request, "Участник не найден.")

        return django.shortcuts.redirect('meropriations:results_new')


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
                                      status="WINNER").count()
        prizers = Team.objects.filter(result__meropriation=meropriation,
                                      status="PRIZER").count()
        participants = all_teams.count() - winners - prizers

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="result_report_{meropriation_id}.csv"'

        writer = csv.writer(response)

        writer.writerow(["Статистика", "Количество"])
        writer.writerow(["Победителей", winners])
        writer.writerow(["Призёров", prizers])
        writer.writerow(["Участников", participants])
        writer.writerow(["Общее количество участников", all_teams.count()])

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


class Notifications(LoginRequiredMixin, django.views.generic.ListView):
    template_name = "meropriations/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        region = self.request.user.region
        if not region:
            return django.shortcuts.redirect('homepage:main')
        return Notification.objects.filter(meropriation__region=region)


class DeleteNotificationView(LoginRequiredMixin, View):
    def post(self, request, notification_id):
        notification = django.shortcuts.get_object_or_404(Notification, id=notification_id)
        notification.delete()

        return redirect('meropriations:notifications')
