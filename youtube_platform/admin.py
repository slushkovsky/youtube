from django.contrib import admin

from .models import Plain


class PlainAdmin(admin.ModelAdmin):
    pass

admin.site.register(Plain, PlainAdmin)
