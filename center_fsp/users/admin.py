import django.contrib.admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

import users.models

django.contrib.admin.site.unregister(Group)

@django.contrib.admin.register(get_user_model())
class UserAdmin(UserAdmin):
    list_display = ("region", "username", "email", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("region", "avatar")}),
    )


@django.contrib.admin.register(users.models.Region)
class RegionAdmin(django.contrib.admin.ModelAdmin):
    pass
