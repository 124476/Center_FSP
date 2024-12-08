from django.db.models import Count, Sum
from django.views.generic import ListView

from meropriations.models import Result, Team, Participant, Meropriation


class RegionStatisticsView(ListView):
    template_name = "stats/regions_stats.html"
    context_object_name = "region_stats"

    def get_queryset(self):
        results = Meropriation.objects.filter(region__isnull=False).values(
            'region__name').annotate(
            total_events=Count('id'),
            total_participants=Sum('count')
        )

        for result in results:
            if result['total_participants'] is None:
                result['total_participants'] = 0

        return results


class UserStatisticsView(ListView):
    template_name = "stats/users_stats.html"
    context_object_name = "user_stats"

    def get_queryset(self):
        results = list(
            Result.objects.filter(
                captain__isnull=False
            ).values('captain__name')
            .annotate(
                total=Count('id')
            )
        )
        return results


class TeamStatisticsView(ListView):
    template_name = "stats/teams_stats.html"
    context_object_name = "team_stats"

    def get_queryset(self):
        results = list(
            Result.objects.filter(
                team__isnull=False
            ).values('team__name')
            .annotate(
                total=Count('id')
            )
        )
        return results
