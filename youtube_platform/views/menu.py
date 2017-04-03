from itertools import groupby
from functools import lru_cache

from youtube_platform.models import Plain, Feature
from youtube_platform.views.modules import ServicePermission

MENU_ITEMS = [
    ('Базовый', ServicePermission.base, [
        ('Комментаторы видео', 'commentators'),
        ('Каналы пользователей сетей', 'user_channels'),
        ('Динамика канала', 'channel_dynamic')
    ]),

    ('Стандарт', ServicePermission.standart, [
        ('ТОП3 видео среди пользователей', 'top3_among_users'),
        ('ТОП3 видео', 'top3_video'),
        ('Коллаборация', 'collaboration'),
        ('Анализ аудитории', 'auditory_analyze'),
        ('Популярные теги', 'popular_tags')
    ]),

    ('Премиум', ServicePermission.premium, [
        ('Подписчики канала', 'channel_subscribers'),
        ('Отслеживание чужой рекламы', 'foreign_ad_track'),
        ('Рассылка сообщений', 'broadcast_message'),
    ])
]


def create_menu_items():
    if hasattr(create_menu_items, '_cache'):
        return getattr(create_menu_items, '_cache')
    else:
        items = [
            (
                plain.title, plain.get_permission(),
                [
                    (f.feature_title, f.feature_name)
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
                (stitle, '/module?feature={}'.format(tag))
                for stitle, tag in subs
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
        'expiry_in_days': request.user.profile.account_type.day_excess,
        'menu_items': menu_items,
        'plains': [p.dict() for p in Plain.get_visible()]
    }
