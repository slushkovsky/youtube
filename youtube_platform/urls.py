"""youtube_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from .serve import serve
from .views.index import handle_index
from .views.plain import handle_plains
from .views.auth import login, logout, register, change_password, forgot_password
from .views.entry_point import entry_point
from .views.profile import profile
from .views.modules.count_roi import process_roi


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^([\w\/\-.]+).(js|css|scss|jpg|png|wof|ttf)[?\w\d]*', serve),
    url(r'^/?$', handle_index),
    url(r'^index', handle_index),
    url(r'^plain', handle_plains),
    url(r'^module', entry_point),
    url(r'^accounts/login.*$', login),
    url(r'^accounts/logout$', logout),
    url(r'^accounts/registration$', register),
    url(r'^accounts/profile$', profile),
    url(r'^accounts/change_password', change_password),
    url(r'^accounts/forgot_password$', forgot_password),
    url(r'^roi', process_roi)
]
