from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import delete, get_thumbnail


class Region(models.Model):
    name = models.CharField(
        verbose_name="регион",
        max_length=150,
        null=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "регион"
        verbose_name_plural = "регионы"

    def __str__(self):
        return self.name


class User(AbstractUser):
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        null=True,
        blank=True,
    )
    region = models.ForeignKey(
        Region,
        verbose_name="регион",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def has_avatar(self):
        return self.avatar and self.avatar.url is not None

    def get_small_avatar(self):
        return get_thumbnail(self.avatar, "80", crop="center").url

    def get_large_avatar(self):
        return get_thumbnail(self.avatar, "200", crop="center").url

    def save(self, *args, **kwargs):
        try:
            old = User.objects.get(pk=self.pk)
            if old.has_avatar() and not self.has_avatar():
                delete(old.avatar)
        except User.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("region",)
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.username