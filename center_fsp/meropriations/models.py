import django.db.models
import django.conf
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class Group(django.db.models.Model):
    name = django.db.models.CharField(
        verbose_name="название",
        max_length=150,
        null=False,
        unique=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "наименование спортивного мероприятия"
        verbose_name_plural = "наименования спортивного мероприятия"

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
    slug = django.db.models.SlugField(
        verbose_name="слаг",
        max_length=200,
        null=True,
    )
    name = django.db.models.CharField(
        verbose_name="название",
        max_length=150,
        unique=False,
        null=True,
    )
    text = django.db.models.TextField(
        null=True,
        verbose_name="текст",
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
        verbose_name="категория",
        null=True,
        on_delete=django.db.models.CASCADE,
        related_name="catalog_items",
    )
    tip = django.db.models.ForeignKey(
        Tip,
        verbose_name="категория",
        null=True,
        on_delete=django.db.models.CASCADE,
        related_name="catalog_items",
    )
    group = django.db.models.ForeignKey(
        Group,
        verbose_name="категория",
        null=True,
        on_delete=django.db.models.CASCADE,
        related_name="catalog_items",
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


class Profile(django.db.models.Model):
    user = django.db.models.OneToOneField(
        django.conf.settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        on_delete=django.db.models.CASCADE,
    )
    group_request = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    tip_request = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    structure_request = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    gender_request = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    tip = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    group = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    structure = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    gender = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    place = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    disciple = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    event_period = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    rows_per_page = django.db.models.CharField(
        max_length=150,
        null=True,
    )
    participants_count = django.db.models.CharField(
        max_length=150,
        null=True,
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "дисциплина"
        verbose_name_plural = "дисциплины"

    def __str__(self):
        return self.id


@receiver(post_save, sender=Meropriation)
def notify_users_on_new_event(sender, instance, created, **kwargs):
    if created:
        subject = "Новое спортивное мероприятие добавлено"
        message = f"Добавлено новое мероприятие: {instance.name}\nСроки проведения: {instance.date_start} - {instance.date_end}\nМесто проведения: {instance.place}"
        recipients = [
            user.email
            for user in User.objects.filter(is_active=True)
            if user.email
        ]

        send_mail(
            subject,
            message,
            django.conf.settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
