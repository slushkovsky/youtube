from itertools import groupby
from functools import lru_cache

from youtube_platform.models import Plain, Feature
from youtube_platform.views.modules import ServicePermission


def create_menu_items():
    if hasattr(create_menu_items, '_cache'):
        return getattr(create_menu_items, '_cache')
    else:
        items = [
            (
                plain.title, plain.get_permission(),
                [
                    (f.feature_title, f.feature_name, f.icon)
                    for f in features
                ]
             )
            for plain, features in groupby(
                Feature.objects.all(), lambda f: f.plain_required
            )
        ]
        setattr(create_menu_items, '_cache', items)
        return items


def create_context_from_request(request):
    menu_items = [
        (
            title, request.user.profile.has_perm(perm),
            [
                (stitle, '/module?feature={}'.format(tag), icon)
                for stitle, tag, icon in subs
            ]
        )
        for title, perm, subs in create_menu_items()
    ]

    return {
        'result': {
            'errors': [],
            'details': {}
        },
        'user_email': request.user.email,
        'permission_level': request.user.profile.account_type.plain.permission_level, 
        'expiry_in_days': request.user.profile.account_type.day_excess,
        'menu_items': menu_items,
        'plains': [p.dict() for p in Plain.get_visible()],
    }
