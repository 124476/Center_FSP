from django.urls import path
from django.views.generic import TemplateView

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
        "results/new/",
        views.ResultCreateView.as_view(),
        name="results_new",
    ),
    path(
        'add-team/',
        views.AddTeamView.as_view(),
        name="add_team"
    ),
    path(
        'delete-participant/<int:participant_id>/',
        views.DeleteParticipantView.as_view(),
        name="delete_participant"
    ),
    path(
        "notifications/",
        views.Notifications.as_view(),
        name="notifications",
    ),
    path(
        'download-templates/',
        TemplateView.as_view(
            template_name="meropriations/download_templates.html"),
        name='download_templates'
    ),
    path(
        'generate-result-report/<int:meropriation_id>/',
        views.GenerateResultReportView.as_view(),
        name="generate_result_report",
    ),
]
