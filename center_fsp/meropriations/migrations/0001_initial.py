# Generated by Django 4.2.16 on 2024-12-10 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Discipline",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="название"
                    ),
                ),
            ],
            options={
                "verbose_name": "дисциплина",
                "verbose_name_plural": "дисциплины",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Meropriation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_published",
                    models.BooleanField(
                        default=False, verbose_name="опубликовано"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150, null=True, verbose_name="название"
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        null=True, verbose_name="описание мероприятия"
                    ),
                ),
                (
                    "count",
                    models.PositiveIntegerField(
                        null=True, verbose_name="количество участников"
                    ),
                ),
                (
                    "place",
                    models.TextField(
                        null=True, verbose_name="место проведения"
                    ),
                ),
                (
                    "date_start",
                    models.DateField(null=True, verbose_name="дата начала"),
                ),
                (
                    "date_end",
                    models.DateField(null=True, verbose_name="дата конца"),
                ),
                (
                    "disciplines",
                    models.ManyToManyField(
                        to="meropriations.discipline",
                        verbose_name="дисциплины",
                    ),
                ),
            ],
            options={
                "verbose_name": "мероприятие",
                "verbose_name_plural": "мероприятия",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Structure",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="название"
                    ),
                ),
            ],
            options={
                "verbose_name": "состав",
                "verbose_name_plural": "составы",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Победитель", "Winner"),
                            ("Призёр", "Prizer"),
                            ("Участник", "Participant"),
                        ],
                        default="Участник",
                        max_length=30,
                        verbose_name="статус мероприятия",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150, null=True, verbose_name="название"
                    ),
                ),
            ],
            options={
                "verbose_name": "команда",
                "verbose_name_plural": "команды",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Tip",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="название"
                    ),
                ),
            ],
            options={
                "verbose_name": "тип соревнования",
                "verbose_name_plural": "типы соревнований",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Result",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "meropriation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meropriations.meropriation",
                        verbose_name="мероприятие",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meropriations.team",
                        verbose_name="команда",
                    ),
                ),
            ],
            options={
                "verbose_name": "результат",
                "verbose_name_plural": "результаты",
            },
        ),
        migrations.CreateModel(
            name="Participant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150, null=True, verbose_name="фио"
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meropriations.team",
                        verbose_name="команда",
                    ),
                ),
            ],
            options={
                "verbose_name": "участник",
                "verbose_name_plural": "участники",
                "ordering": ("team__name",),
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.CharField(
                        max_length=150, verbose_name="текст уведомления"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="активен"),
                ),
                (
                    "meropriation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meropriations.meropriation",
                        verbose_name="мероприятие",
                    ),
                ),
            ],
            options={
                "verbose_name": "уведомление",
                "verbose_name_plural": "уведомления",
            },
        ),
    ]
