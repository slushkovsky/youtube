# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-28 22:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube_platform', '0010_plain'),
    ]

    operations = [
        migrations.AddField(
            model_name='plain',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]