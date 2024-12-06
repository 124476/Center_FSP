from django.urls import path

import meropriations_calendar.views

app_name = "calendar"
urlpatterns = [
    path("", meropriations_calendar.views.Home.as_view(), name="main"),
]
