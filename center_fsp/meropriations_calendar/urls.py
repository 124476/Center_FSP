from django.urls import path

import meropriations_calendar.views

app_name = "calendar"
urlpatterns = [
    path("", meropriations_calendar.views.Home.as_view(), name="main"),
    path(
        "detail/<int:event_id>/",
        meropriations_calendar.views.event_detail,
        name="detail_event",
    ),
    path(
        "results/<int:event_id>/",
        meropriations_calendar.views.event_results,
        name="event_results",
    ),
]
