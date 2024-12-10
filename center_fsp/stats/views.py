from django.views.generic import TemplateView
from django.db.models import Count

from meropriations.models import Result, Team, Participant, Meropriation
from users.models import Region


class RegionStatisticsView(TemplateView):
    template_name = "stats/regions_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Аналитика по регионам
        regions = Region.objects.all()
        region_names = []
        region_events = []

        total_events = 0
        total_participants = 0

        for region in regions:
            meropriations = Meropriation.objects.filter(region=region)

            event_count = meropriations.count()
            participant_count = 0

            for meropriation in meropriations:
                participant_count += Participant.objects.filter(
                    team__result__meropriation=meropriation,
                ).count()

            region_names.append(region.name)
            region_events.append(event_count)

            total_events += event_count
            total_participants += participant_count

        forecast_years = [2024, 2025, 2026, 2027, 2028]
        forecast_values = [total_events * (1.1 ** i) // 1 for i in range(len(forecast_years))]

        context['total_regions'] = regions.count()
        context['total_events'] = total_events
        context['total_participants'] = total_participants
        context['region_names'] = region_names
        context['region_events'] = region_events
        context['forecast_years'] = forecast_years
        context['forecast_values'] = forecast_values

        return context


class UserStatisticsView(TemplateView):
    template_name = "stats/users_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        participants = Participant.objects.all()
        participant_names = []
        participant_events = []

        total_events = 0

        for participant in participants:
            event_count = Result.objects.filter(team__participant=participant).count()
            participant_names.append(participant.name)
            participant_events.append(event_count)
            total_events += event_count

        forecast_years = [2024, 2025, 2026, 2027, 2028]
        forecast_values = [total_events * (1.05 ** i) // 1 for i in range(len(forecast_years))]

        meropriations = Meropriation.objects.all()
        event_count = meropriations.count()

        context['total_participants'] = participants.count()
        context['total_events'] = event_count
        context['participant_names'] = participant_names[:10]
        context['participant_events'] = participant_events[:10]
        context['forecast_years'] = forecast_years
        context['forecast_values'] = forecast_values

        return context


class TeamStatisticsView(TemplateView):
    template_name = "stats/teams_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получение данных о командах с количеством мероприятий и участников
        teams_with_counts = (
            Team.objects.annotate(
                event_count=Count('result'),  # Количество мероприятий
                participant_count=Count('participant')  # Количество участников
            )
            .order_by('-event_count')[:10]  # Топ-10 команд
        )

        team_names = [team.name for team in teams_with_counts]
        team_events = [team.event_count for team in teams_with_counts]
        team_participants = [team.participant_count for team in teams_with_counts]
        total_events = sum(team_events)

        # Прогнозирование
        forecast_years = [2024, 2025, 2026, 2027, 2028]
        forecast_values = [round(total_events * (1.1 ** i)) for i in range(len(forecast_years))]

        # Общее количество мероприятий
        total_event_count = Meropriation.objects.count()

        context.update({
            'total_teams': Team.objects.count(),
            'total_events': total_event_count,
            'team_names': team_names,
            'team_events': team_events,
            'team_participants': team_participants,  # Добавлено
            'forecast_years': forecast_years,
            'forecast_values': forecast_values,
        })

        return context