from django.urls import path

from stats.views import (
    RegionStatisticsView,
    TeamStatisticsView,
    UserStatisticsView,
)

app_name = "stats"
urlpatterns = [
    path("regions/", RegionStatisticsView.as_view(), name="region_statistics"),
    path("users/", UserStatisticsView.as_view(), name="user_statistics"),
    path("teams/", TeamStatisticsView.as_view(), name="team_statistics"),
]
