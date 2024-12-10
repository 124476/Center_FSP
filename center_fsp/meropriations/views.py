import csv

from allauth.core.internal.httpkit import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import django.shortcuts
from django.urls import reverse_lazy
from django.views.generic import DetailView, View
from django.views.generic.edit import CreateView
import django.views.generic
import django.forms

from meropriations.models import Meropriation, Result, Notification, Team, \
    Participant
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

        meropriations = Meropriation.objects.filter(region=user_region,
                                                    status='Принят')

        meropriation_id = request.POST.get('meropriation')
        try:
            meropriation = Meropriation.objects.get(id=meropriation_id)
        except Meropriation.DoesNotExist:
            messages.error(request, "Выбранное мероприятие некорректно.")
            return redirect('meropriations:results_new')

        files = request.FILES.getlist('file')
        if not files:
            messages.error(request, "Вы не загрузили файлы.")
            return redirect('meropriations:results_new')

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
                return redirect('meropriations:results_new')

        results = Result.objects.filter(meropriation=meropriation).all()

        if not results:
            messages.error(request, "Нет результатов")
            return redirect('meropriations:results_new')

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
            messages.error(request, "Ошибка: все поля обязательны для заполнения.")
            return redirect('meropriations:add_team')

        try:
            meropriation = Meropriation.objects.get(id=meropriation_id)
        except Meropriation.DoesNotExist:
            messages.error(request, "Выбранное мероприятие некорректно.")
            return redirect('meropriations:add_team')

        Team.objects.create(name=team_name)

        messages.success(request, f"Команда '{team_name}' успешно добавлена на мероприятие '{meropriation.name}'")
        return redirect('meropriations:results_new')


class DeleteParticipantView(View):
    def post(self, request, participant_id):
        try:
            participant = Participant.objects.get(id=participant_id)
            participant.delete()
            messages.success(request, "Участник успешно удален.")
        except Participant.DoesNotExist:
            messages.error(request, "Участник не найден.")

        return redirect('meropriations:results_new')


class GenerateResultReportView(DetailView):
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

        meropriation_id = request.POST.get('meropriation')
        try:
            meropriation = Meropriation.objects.get(id=meropriation_id)
        except Meropriation.DoesNotExist:
            messages.error(request, "Выбранное мероприятие некорректно.")
            return redirect('meropriations:new_results')

        files = request.FILES.getlist('file')
        if not files:
            messages.error(request, "Вы не загрузили файлы.")
            return redirect('meropriations:new_results')

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
                return redirect('meropriations:new_results')

        messages.success(request, "Файлы успешно загружены и обработаны.")
        return redirect('meropriations:meropriations')

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
