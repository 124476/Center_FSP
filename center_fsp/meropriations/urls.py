from django.urls import path

from meropriations import views

app_name = "meropriations"

urlpatterns = [
    path(
        "meropriations/",
        views.MeropriationList.as_view(),
        name="meropriations",
    ),
    path(
        "meropriations/<int:pk>/",
        views.MeropriationList.as_view(),
        name="meropriation_detail",
    ),
    path(
        "meropriations/new/",
        views.MeropriationList.as_view(),
        name="meropriation_new",
    ),
]
