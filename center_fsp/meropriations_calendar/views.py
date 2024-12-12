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
        queryset = Meropriation.objects.filter(is_published=True)

        # Apply filters
        filters = {
            'tip': 'tip__name',
            'structure': 'structure__name',
            'gender': 'text__icontains',
            'region': 'region__name',
            'discipline': 'disciplines__name__icontains'
        }

        for key, field in filters.items():
            value = self.request.GET.get(key)
            if value:
                queryset = queryset.filter(**{field: value})

        # Filter by date range (if provided)
        date_param = self.request.GET.get('date')
        if date_param:
            try:
                input_date = datetime.strptime(date_param, "%Y-%m-%d").date()
                last_day_of_month = input_date.replace(
                    day=calendar.monthrange(input_date.year, input_date.month)[
                        1])
                queryset = queryset.filter(date_end__gte=input_date,
                                           date_start__lte=last_day_of_month)
            except ValueError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Prepare calendar data
        queryset = self.get_queryset()
        grouped_events = defaultdict(list)

        for event in queryset:
            start_date = event.date_start
            end_date = event.date_end
            current_date = start_date
            while current_date <= end_date:
                grouped_events[current_date.day].append(event)
                current_date += timedelta(days=1)

        weeks = []
        current_week = []
        for day in range(1, 32):
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
