from django.urls import path

from meropriations import views

app_name = "meropriations"

urlpatterns = [
    path(
        "",
        views.MeropriationList.as_view(),
        name="meropriations",
    ),
    path(
        "<int:pk>/",
        views.MeropriationDetailView.as_view(),
        name="meropriation_detail",
    ),
    path(
        "new/",
        views.MeropriationCreateView.as_view(),
        name="meropriation_new",
    ),
    path(
        "results/",
        views.ResultList.as_view(),
        name="results",
    ),
    path(
        "results/new/",
        views.ResultCreateView.as_view(),
        name="results_new",
    )
]
