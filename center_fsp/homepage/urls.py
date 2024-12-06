from django.urls import path

import homepage.views

app_name = "homepage"
urlpatterns = [
    path("", homepage.views.Home.as_view(), name="main"),
    path(
        "update_db/", homepage.views.UpdateDBView.as_view(), name="update_db"
    ),
]
