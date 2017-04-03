# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-25 16:49
from __future__ import unicode_literals

from django.db import migrations

from youtube_platform.service_permission import ServicePermission


def create_permissions(apps, *args, **kwargs):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')

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


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(create_permissions)
    ]
