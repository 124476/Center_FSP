import django.contrib.admin

import meropriations.models


@django.contrib.admin.register(meropriations.models.Structure)
class StructureAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(meropriations.models.Tip)
class TipAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(meropriations.models.Discipline)
class DisciplineAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(meropriations.models.Result)
class ResultAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(meropriations.models.Participant)
class ParticipantAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(meropriations.models.Team)
class TeamAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(meropriations.models.Notification)
class NotificationAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(meropriations.models.Meropriation)
class MeropriationAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        meropriations.models.Meropriation.region.field.name,
        meropriations.models.Meropriation.name.field.name,
        meropriations.models.Meropriation.is_published.field.name,
    )
