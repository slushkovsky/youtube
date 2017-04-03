# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-30 01:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube_platform', '0013_auto_20170329_2310'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=256)),
                ('parameter_title', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='feature',
            name='feature_title',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feature',
            name='in_menu',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]