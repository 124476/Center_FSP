__all__ = ()
import django.forms

from feedback.models import Feedback, FeedbackFile, UserProfile


class UserProfileForm(django.forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = UserProfile
        fields = (
            UserProfile.name.field.name,
            UserProfile.mail.field.name,
        )

        labels = {
            UserProfile.name.field.name: "Имя",
            UserProfile.mail.field.name: "Почта",
        }

        help_texts = {
            UserProfile.name.field.name: "Введите свою имя",
            UserProfile.mail.field.name: "Введите свою почту",
        }

        widgets = {
            UserProfile.name.field.name: django.forms.TextInput(),
            UserProfile.mail.field.name: django.forms.EmailInput(),
        }


class FeedbackForm(django.forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Feedback
        fields = (Feedback.text.field.name,)

        labels = {
            Feedback.text.field.name: "Текст",
        }

        help_texts = {
            Feedback.text.field.name: "Введите свой отзыв",
        }

        exclude = (Feedback.created_on.field.name,)

        widgets = {
            Feedback.text.field.name: django.forms.Textarea(),
        }


class MultipleFileInput(django.forms.ClearableFileInput):
    allow_multiple_selected = True


class FeedbackFileForm(django.forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = FeedbackFile

        fields = (FeedbackFile.file.field.name,)
        labels = {
            FeedbackFile.file.field.name: "Загрузить файлы",
        }
        help_texts = {
            FeedbackFile.file.field.name: "Загрузка файлы",
        }
        widgets = {
            FeedbackFile.file.field.name: MultipleFileInput(
                attrs={
                    "multiple": True,
                },
            ),
        }

    # Проверяем размер всех файлов
    def clean_file(self):
        files = self.cleaned_data.get("file")
        if files:
            for file in self.files.getlist("file"):
                if file.size > 20 * 1024 * 1024:  # 20 MB
                    raise django.forms.ValidationError(
                        f"Размер файла {file.name} превышает лимит 20 МБ.",
                    )

        return files
