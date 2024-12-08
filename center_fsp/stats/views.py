from django.views.generic import ListView

from meropriations.models import Result, Team, Participant, Meropriation
from users.models import Region

from django.db.models import Count


class RegionStatisticsView(ListView):
    template_name = "stats/regions_stats.html"
    context_object_name = "region_stats"

    def get_queryset(self):
        regions = []

        all_regions = Region.objects.all()

        for region in all_regions:
            meropriations = Meropriation.objects.filter(region=region)

            total_participants = 0
            for meropriation in meropriations:
                total_participants += Participant.objects.filter(
                    team__result__meropriation=meropriation,
                ).count()

            regions.append({
                "region": region.name,
                "total_events": meropriations.count(),
                "total_participants": total_participants,
            })

        return regions


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
