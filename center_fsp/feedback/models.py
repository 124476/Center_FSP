import django.db.models
import django.utils.safestring


class Feedback(django.db.models.Model):
    created_on = django.db.models.DateTimeField(
        auto_now_add=True,
    )
    text = django.db.models.TextField(
        verbose_name="текст",
        null=False,
    )

    class Meta:
        verbose_name = "ответ"
        verbose_name_plural = "ответы"

    def __str__(self):
        return str(self.id)


class UserProfile(django.db.models.Model):
    name = django.db.models.CharField(
        verbose_name="имя",
        max_length=100,
        null=True,
        blank=True,
        help_text="max 100 символов",
    )
    mail = django.db.models.EmailField(
        verbose_name="почта",
        max_length=100,
        help_text="max 100 символов",
    )
    author = django.db.models.OneToOneField(
        Feedback,
        related_name="profile",
        related_query_name="user",
        null=True,
        on_delete=django.db.models.CASCADE,
    )

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def __str__(self):
        return f"Профиль пользователя {self.name}, {self.mail}"


class FeedbackFile(django.db.models.Model):
    def get_upload_file(self, filename):
        return f"uploads/{self.feedback_id}/{filename}"

    feedback = django.db.models.ForeignKey(
        Feedback,
        verbose_name="Обратная связь",
        on_delete=django.db.models.SET_NULL,
        null=True,
        related_name="fields",
    )
    file = django.db.models.FileField(
        verbose_name="файлы",
        upload_to=get_upload_file,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "файл"
        verbose_name_plural = "файлы"

    def __str__(self):
        return str(self.file)
