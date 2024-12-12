from datetime import datetime, timedelta
import calendar
import numpy as np
from collections import defaultdict

from django.core.paginator import Paginator
from django.http import Http404
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404

from meropriations.models import Meropriation, Result
import meropriations.models


class Home(ListView):
    template_name = "meropriations_calendar/main.html"

    def get_queryset(self):
        queryset = meropriations.models.Meropriation.objects.all()

        queryset = queryset.filter(is_published=True)

        tip = self.request.GET.get("tip")
        structure = self.request.GET.get("structure")
        region = self.request.GET.get("region")
        discipline = self.request.GET.get("discipline")
        date = self.request.GET.get("date")

        if discipline:
            queryset = queryset.filter(disciplines__name__icontains=discipline)

        if tip:
            queryset = queryset.filter(tip__name=tip)

        if structure:
            queryset = queryset.filter(structure__name=structure)

        if region:
            queryset = queryset.filter(region__name=region)

        if date:
            try:
                input_date = datetime.strptime(date, "%Y-%m-%d").date()
                input_date.replace(
                    day=calendar.monthrange(input_date.year, input_date.month)[
                        1]
                )

                last_day_of_month = input_date.replace(
                    day=calendar.monthrange(input_date.year, input_date.month)[
                        1]
                )

                queryset = queryset.filter(
                    date_end__gte=input_date,
                    date_start__lte=last_day_of_month
                )
            except ValueError:
                pass
        else:
            input_dt = datetime.today()
            input_date = input_dt.replace(day=1)
            input_date.replace(
                day=calendar.monthrange(input_date.year, input_date.month)[
                    1]
            )

            last_day_of_month = input_date.replace(
                day=calendar.monthrange(input_date.year, input_date.month)[
                    1]
            )

            queryset = queryset.filter(
                date_end__gte=input_date,
                date_start__lte=last_day_of_month
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["page_obj"] = self.get_queryset
        context["disciplines"] = (
            meropriations.models.Discipline.objects.values_list(
                "name", flat=True
            )
            .distinct()
            .order_by("name")
        )
        context["tips"] = (
            meropriations.models.Meropriation.objects.values_list(
                "tip__name", flat=True
            )
            .distinct()
            .order_by("tip__name")
        )
        context["structures"] = (
            meropriations.models.Meropriation.objects.values_list(
                "structure__name", flat=True
            )
            .distinct()
            .order_by("structure__name")
        )
        context["regions"] = (
            meropriations.models.Meropriation.objects.values_list(
                "region__name", flat=True
            )
            .distinct()
            .order_by("region__name")
        )
        context["request"] = self.request
        context["day_week_list"] = [
            'Понедельник',
            'Вторник',
            'Среда',
            'Четверг',
            'Пятница',
            'Суббота',
            'Воскресенье'
        ]

        date = self.request.GET.get("date")

        if date:
            try:
                input_date = datetime.strptime(date, "%Y-%m-%d").date()
                date_delta = input_date.weekday()
            except ValueError:
                input_date = datetime.now()
                date_delta = input_date.weekday()
        else:
            input_date = datetime.now()
            date_delta = input_date.weekday()

        queryset = self.get_queryset()
        grouped_events = defaultdict(list)
        for event in queryset:
            start_date = event.date_start
            end_date = event.date_end
            current_date = start_date
            while current_date <= end_date:
                grouped_events[current_date.day].append(event)
                current_date += timedelta(days=1)

        _, days_in_month = calendar.monthrange(input_date.year,
                                               input_date.month)
        weeks = []
        current_week = [0] * date_delta
        for day in range(1, days_in_month + 1):
            events_for_day = grouped_events.get(day, [])
            current_week.append({'date': day, 'events': events_for_day})

            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []

        if current_week:
            weeks.append(current_week)

        context['calendar_weeks'] = weeks
        return context


def event_results(request, event_id):
    meropriation = get_object_or_404(Meropriation, id=event_id)

    results = Result.objects.filter(meropriation=meropriation)
    if not results.exists():
        raise Http404("Результаты для данного мероприятия не найдены.")

    team_sizes = [team.participant_set.count() for team in [result.team for result in results]]
    avg_participants = np.mean(team_sizes) if team_sizes else 0
    max_participants = np.max(team_sizes) if team_sizes else 0
    min_participants = np.min(team_sizes) if team_sizes else 0

    if len(team_sizes) > 1:
        x = np.arange(len(team_sizes))
        y = np.array(team_sizes)
        coeffs = np.polyfit(x, y, 1)
        predicted_teams = max(0, int(np.polyval(coeffs, len(team_sizes))))
    else:
        predicted_teams = len(team_sizes)

    team_names = [result.team.name for result in results]

    context = {
        "meropriation": meropriation,
        "avg_participants": avg_participants,
        "max_participants": max_participants,
        "min_participants": min_participants,
        "predicted_teams": predicted_teams,
        "team_names": team_names,
        "team_sizes": team_sizes,
    }

    return render(request, "meropriations_calendar/event_results.html", context)


def event_detail(request, event_id):
    meropriation = get_object_or_404(Meropriation, id=event_id)

    context = {
        "meropriation": meropriation,
    }

    return render(request, "meropriations_calendar/event_detail.html", context)
