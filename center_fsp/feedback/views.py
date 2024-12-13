__all__ = ()
import django.conf
import django.contrib
import django.core.mail
import django.db.models
import django.http
import django.shortcuts
import django.utils
import django.views.generic

import feedback.forms
import feedback.models


class FeedbackForm(django.views.generic.FormView):
    template_name = "feedback/feedback.html"
    form_class = feedback.forms.FeedbackForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_form"] = kwargs.get(
            "author_form",
            feedback.forms.UserProfileForm(),
        )
        context["content_form"] = kwargs.get(
            "content_form",
            feedback.forms.FeedbackForm(),
        )
        context["files_form"] = kwargs.get(
            "files_form",
            feedback.forms.FeedbackFileForm(),
        )
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            self.get_context_data(
                author_form=feedback.forms.UserProfileForm(),
                content_form=feedback.forms.FeedbackForm(),
                files_form=feedback.forms.FeedbackFileForm(),
            ),
        )

    def post(self, request, *args, **kwargs):
        author_form = feedback.forms.UserProfileForm(request.POST or None)
        content_form = feedback.forms.FeedbackForm(request.POST or None)
        files_form = feedback.forms.FeedbackFileForm(request.POST or None)

        if author_form.is_valid() and content_form.is_valid():
            feedback_item = content_form.save()
            author_feedback = author_form.save(commit=False)
            author_feedback.author = feedback_item
            author_feedback.save()

            files = request.FILES.getlist("file")
            for f in files:
                feedback.forms.FeedbackFile.objects.create(
                    feedback=feedback_item,
                    file=f,
                )

            django.contrib.messages.success(
                request,
                "Форма успешно отправлена.",
            )

            return django.shortcuts.redirect("feedback:feedback")

        django.contrib.messages.error(
            request,
            "Пожалуйста, исправьте ошибки в форме.",
        )
        return self.render_to_response(
            self.get_context_data(
                author_form=author_form,
                content_form=content_form,
                files_form=files_form,
            ),
        )


class FeedbackList(django.views.generic.ListView):
    template_name = "feedback/feedback_list.html"
    context_object_name = "feedbacks"

    def get_queryset(self):
        feedbacks = feedback.models.Feedback.objects.all()
        return feedbacks
