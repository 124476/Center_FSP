import django.views.generic
from django.core.exceptions import PermissionDenied
from django.views import View

import meropriations


class Home(django.views.generic.ListView):
    template_name = "homepage/main.html"
    context_object_name = "items"
    queryset = [
        {
            "id": 1,
            "name": "first",
        },
        {
            "id": 2,
            "name": "second",
        },
    ]


class UpdateDBView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied(
                "У вас недостаточно прав для выполнения этой операции."
            )
        meropriations.parser.import_pdf()
        return django.shortcuts.redirect("calendar:main")
