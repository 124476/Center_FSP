# Generated by Django 4.2.16 on 2024-12-11 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("meropriations", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notification",
            name="is_active",
        ),
    ]
