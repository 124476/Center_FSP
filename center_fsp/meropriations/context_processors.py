import django.utils.timezone

import meropriations.models


def get_today_meropriations(request):
    user = request.user

    objects = meropriations.models.Meropriation.objects.all()

    today_date = django.utils.timezone.localdate()

    if user.is_authenticated:
        if user.profile.tip_request:
            objects = objects.filter(tip__name=user.profile.tip_request)

        if user.profile.group_request:
            objects = objects.filter(group__name=user.profile.group_request)

        if user.profile.structure_request:
            objects = objects.filter(
                structure__name=user.profile.structure_request,
            )

        if user.profile.gender_request:
            if user.profile.gender_request == "Муж.":
                objects = (
                    objects.filter(text__icontains="юниоры")
                    | objects.filter(text__icontains="мужчины")
                    | objects.filter(text__icontains="юноши")
                    | objects.filter(text__icontains="мальчики")
                )
            else:
                objects = (
                    objects.filter(text__icontains="женщины")
                    | objects.filter(text__icontains="юниорки")
                    | objects.filter(text__icontains="девушки")
                    | objects.filter(text__icontains="девочки")
                )

    meropriation_list = objects.filter(date_start=today_date).only(
        "id",
        "name",
        "date_start",
        "date_end",
    )

    meropriations_list = [
        {
            "name": meropriation.name,
            "date_start": meropriation.date_start,
            "date_end": meropriation.date_end,
        }
        for meropriation in meropriation_list
    ]
    return {
        "meropriations": meropriations_list,
    }


__all__ = ()
