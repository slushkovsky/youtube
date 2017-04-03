# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 23:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.db.migrations import RunPython

from moneyed import Money, RUB
from youtube_platform.models import Plain


BASE_DESCR = """
Получение комментов
Умный поиск
Получени каналов из файла с ссылками на соц.сети
Динамика любого канала
"""

STANDART_DESCR = """
Получение тех,кто лайкнул видео
Больше фильтров в умном поиске
ТОП 3 из понравившихся
Нет ограничений в функции Динамика Канала
Коллаборация
Самые популярные теги
Аналитика аудитории
"""

PREMIUM = """
Получение подписчиков
Все фильтры в умном поиске!
Снятие ограничений с анализа аудитории
Перевод базы каналов в базу соц.сетей
Пробуждение неактивной аудитории пользователя
Вшитая реклама
Слежка за конкурентами
Подсчёт ROI
"""

PLATINUM = """
Рассылка сообщений
"""

PLAINS = [
    ('Базовый', BASE_DESCR, Money(500, RUB), 500, False, 'fa-home', 1),
    ('Стандарт', STANDART_DESCR, Money(700, RUB), 700, False, 'fa-rocket', 2),
    ('Премиум', PREMIUM, Money(900, RUB), 900, False, 'fa-diamond', 3),
    ('Платинум', PLATINUM, Money(1500, RUB), 1500, True, 'fa-diamond', 4)
]


def add_plains(apps, *args, **kwargs):
    for title, descr, price, ql, hidden, icon, permission_level in PLAINS:
        Plain.objects.create(
            title=title, description=descr, price=price, hidden=hidden,
            quota_limit=ql, fa_icon_name=icon,
            permission_level=permission_level
        )


class Migration(migrations.Migration):

    dependencies = [
        ('youtube_platform', '0012_plain_quota_limit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accounttype',
            name='permission_level',
        ),
        migrations.RemoveField(
            model_name='accounttype',
            name='quota_limit',
        ),
        migrations.AddField(
            model_name='accounttype',
            name='plain',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='youtube_platform.Plain'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plain',
            name='fa_icon_name',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plain',
            name='permission_level',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        RunPython(add_plains, lambda *args: None)
    ]