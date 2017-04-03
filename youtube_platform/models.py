import datetime
import json
from uuid import uuid4

import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import Permission
from django.db.models import ManyToManyField
from django.db.models import (
    Model, OneToOneField, CASCADE, URLField, BooleanField,
    CharField, DateTimeField, IntegerField, ForeignKey, TextField, UUIDField,
)
from django.db.models.base import ObjectDoesNotExist
from djmoney.models.fields import MoneyField

from youtube_platform.service_permission import ServicePermission


class Plain(Model):
    title = CharField(max_length=512)
    description = TextField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='RUB')
    hidden = BooleanField(default=False)
    quota_limit = IntegerField(default=1000)
    permission_level = IntegerField()

    fa_icon_name = CharField(max_length=128)

    @classmethod
    def get_visible(cls):
        return cls.objects.filter(hidden=False).all()

    def get_icon(self):
        return self.fa_icon_name

    def get_permission(self):
        return self.LEVEL_TO_PERMISSION[self.id]

    @classmethod
    def get_by_permission(cls, perm):
        return cls.objects.get(permission_level=cls.PERMISSION_TO_LEVEL[perm])

    def dict(self):
        return {
            'title': self.title,
            'description': [d for d in self.description.splitlines() if len(d) > 0],
            'price': self.price,
            'icon': self.fa_icon_name,
            'codename': str(self.id)
        }

    LEVEL_TO_PERMISSION = {
        1: ServicePermission.base,
        2: ServicePermission.standart,
        3: ServicePermission.premium
    }

    PERMISSION_TO_LEVEL = {
        v: k for k, v in LEVEL_TO_PERMISSION.items()
    }


class AccountType(Model):
    expiry_at = DateTimeField()
    quota_exes = IntegerField(default=0)

    plain = ForeignKey(Plain)

    @property
    def day_excess(self):
        now = pytz.utc.localize(datetime.datetime.now())
        delta = self.expiry_at - now
        return delta.days

    @staticmethod
    def create_perm(permission: ServicePermission, expiry_at):
        return AccountType.objects.create(
            plain=Plain.get_by_permission(permission), expiry_at=expiry_at
        )


class Profile(Model):
    user = OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile', on_delete=CASCADE
    )
    channel_url = URLField()
    channel_id = CharField(max_length=255)

    account_type = OneToOneField(AccountType, on_delete=CASCADE)

    def has_perm(self, permission: ServicePermission):
        now_aware = pytz.utc.localize(datetime.datetime.now())
        if self.account_type.expiry_at < now_aware:
            return False

        plain = Plain.get_by_permission(permission)
        current_plain = self.account_type.plain
        return current_plain.permission_level >= plain.permission_level

    def add_perm(self, permission: ServicePermission, expiry_at=None):
        if expiry_at is None:
            expiry_at = pytz.utc.localize(datetime.datetime.now())
            expiry_at += datetime.timedelta(days=30)
        self.account_type.plain = Plain.get_by_permission(permission)
        self.account_type.expiry_at = expiry_at
        self.account_type.save()
        self.save()

    @staticmethod
    def create_with_permission(user, channel_url, permission):
        now_aware = pytz.utc.localize(datetime.datetime.now())
        now_aware += relativedelta(month=1)
        profile = Profile.objects.create(
            channel_url=channel_url, account_type=AccountType.create_perm(
                permission, now_aware
            ), user=user
        )
        return profile


class MessageBroadcastTask(Model):
    user = ForeignKey(Profile, on_delete=CASCADE)
    recipients = CharField(max_length=1000)
    message = CharField(max_length=1000)
    done = BooleanField()
    success = BooleanField()
    datetime = DateTimeField(auto_now_add=True)


class FeatureParameter(Model):
    parameter_name = CharField(max_length=256)
    parameter_title = CharField(max_length=256)

    @classmethod
    def get_by_name(cls, name):
        return cls.objects.get(parameter_name=name)


class Feature(Model):
    feature_name = CharField(max_length=256)
    quota_cost = IntegerField(default=0)
    feature_title = CharField(max_length=256)
    in_menu = BooleanField(default=True)
    plain_required = ForeignKey(Plain)
    parameters = ManyToManyField(FeatureParameter, related_name='feature')

    @classmethod
    def get_by_name(cls, name):
        return cls.objects.get(feature_name=name)


class FeatureUsage(Model):
    datetime_used = DateTimeField(auto_now_add=True)
    feature = ForeignKey(Feature, related_name='usage_history')
    parameters = TextField()
    user = ForeignKey(Profile, related_name='operations_history')

    def dict(self):
        parametrs = []
        if len(self.parameters) > 0:
            p = json.loads(self.parameters)
            for n, v in p.items():
                if isinstance(v, (list, dict, tuple)):
                    if len(v) == 0:
                        continue
                    elif len(v) == 1:
                        if v[0] == '0':
                            continue
                        else:
                            v = v[0]
                else:
                    if v == 0:
                        continue

                try:
                    feature = FeatureParameter.get_by_name(n)
                except FeatureParameter.DoesNotExist:
                    continue

                parametrs += [{
                    'title': feature.parameter_title,
                    'value': v
                }]

        return {
            'datetime_used': self.datetime_used,
            'feature': self.feature,
            'parameters': parametrs,
            'user': self.user
        }


class ROILink(Model):
    user = ForeignKey(Profile)
    link = URLField()
    label = CharField(max_length=256)
    uuid = UUIDField(default=uuid4)
    visits = IntegerField(default=0)
