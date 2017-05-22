from enum import Enum


class ServicePermission(Enum):
    initial = 'auth.ytools.initial'
    base = 'auth.ytools.base'
    standart = 'auth.ytools.standart'
    premium = 'auth.ytools.premium'

    def value_without_module(self):
        return self.value[len('auth.'):]
