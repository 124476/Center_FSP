from django.urls import path

from feedback import views

app_name = "feedback"
urlpatterns = [
    path(
        "",
        views.FeedbackForm.as_view(),
        name="feedback",
    ),
    path(
        "feedbacks/",
        views.FeedbackList.as_view(),
        name="feedbacks",
    ),
]
