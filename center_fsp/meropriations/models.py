import django.db.models
import django.conf
from django.utils.translation import gettext_lazy as _

import users.models


class Structure(django.db.models.Model):
    name = django.db.models.CharField(
        verbose_name="название",
        max_length=150,
        null=False,
        unique=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "состав"
        verbose_name_plural = "составы"

    def __str__(self):
        return self.name[:15]


class Tip(django.db.models.Model):
    name = django.db.models.CharField(
        verbose_name="название",
        max_length=150,
        null=False,
        unique=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "тип соревнования"
        verbose_name_plural = "типы соревнований"

    def __str__(self):
        return self.name[:15]


class Discipline(django.db.models.Model):
    name = django.db.models.CharField(
        verbose_name="название",
        max_length=150,
        null=False,
        unique=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "дисциплина"
        verbose_name_plural = "дисциплины"

    def __str__(self):
        return self.name[:15]


class Meropriation(django.db.models.Model):
    class Status(django.db.models.TextChoices):
        CONSIDERATION = _("consideration")
        ACCEPT = _("acceptance")

    region = django.db.models.ForeignKey(
        users.models.Region,
        verbose_name="регион",
        null=True,
        on_delete=django.db.models.CASCADE,
        related_name="meropriation_regions",
    )
    status = django.db.models.CharField(
        verbose_name="статус мероприятия",
        choices=Status.choices,
        default=Status.CONSIDERATION,
        max_length=30,
    )
    name = django.db.models.CharField(
        verbose_name="название",
        max_length=150,
        unique=False,
        null=True,
    )
    text = django.db.models.TextField(
        null=True,
        verbose_name="описание мероприятия",
    )
    count = django.db.models.PositiveIntegerField(
        null=True,
        verbose_name="количество участников",
    )
    place = django.db.models.TextField(
        null=True,
        verbose_name="место проведения",
    )
    normal_place = django.db.models.TextField(
        null=True,
        verbose_name="нормальное место проведения",
    )
    structure = django.db.models.ForeignKey(
        Structure,
        verbose_name="состав",
        null=True,
        on_delete=django.db.models.CASCADE,
        related_name="meropriation_structures",
    )
    tip = django.db.models.ForeignKey(
        Tip,
        verbose_name="тип соревнования",
        null=True,
        on_delete=django.db.models.CASCADE,
        related_name="meropriation_tips",
    )
    disciplines = django.db.models.TextField(
        verbose_name="дисциплины",
        null=True,
    )
    date_start = django.db.models.DateField(
        verbose_name="дата начала",
        null=True,
    )
    date_end = django.db.models.DateField(
        verbose_name="дата конца",
        null=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "мероприятие"
        verbose_name_plural = "мероприятия"

    def __str__(self):
        return self.name


class Result(django.db.models.Model):
    meropriation = django.db.models.ForeignKey(
        Meropriation,
        verbose_name="мероприятие",
        on_delete=django.db.models.CASCADE,
    )

    class Meta:
        verbose_name = "результат"
        verbose_name_plural = "результаты"

    def __str__(self):
        return self.meropriation
