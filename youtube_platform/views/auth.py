from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.views import (
    login as auth_login, logout as auth_logout, password_reset,
    password_reset_done, password_reset_confirm, password_reset_complete
)
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from youtube_platform.service_permission import ServicePermission
from ..models import Profile, User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    channel_url = forms.URLField() 

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'channel_url')

    def save(self, commit=True):
        user = User.objects.create(self.cleaned_data['email'], self.cleaned_data['password1']) 
        p = Profile.create_with_permission(user, ServicePermission.initial)
        p.channel_url = self.cleaned_data['channel_url']
        p.save() 

        return user


@csrf_exempt
def login(request):
    return auth_login(
        request, 'accounts/login.html', redirect_field_name='success_redirect'
    )


@login_required
def logout(request):
    return auth_logout(request)


def forgot_password(request):
    if 'status' in request.GET:
        if request.GET['status'] == 'done':
            return password_reset_done(
                request, 'accounts/forgot_password.html', {'done': True}
            )
        elif request.GET['status'] == 'confirm':
            return password_reset_confirm(
                request, request.GET['uid'], request.GET['token'],
                'accounts/forgot_password.html',
                extra_context={'confirm': True},
                post_reset_redirect='/accounts/forgot_password?status=complete'
            )
        elif request.GET['status'] == 'complete':
            return password_reset_complete(
                request, 'accounts/forgot_password.html', {'complete': True}
            )
    else:
        return password_reset(
            request, 'accounts/forgot_password.html',
            post_reset_redirect='/accounts/forgot_password?status=done',
            email_template_name='accounts/reset_password_email.html',
            subject_template_name='accounts/reset_password_email_subject.txt'
        )


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/login')
    else:
        form = RegistrationForm()

    args = {
        'form': form
    }

    return render(request, 'accounts/register.html', args)

def confirm_email(request): 
	return redirect('/accounts/profile')

@login_required(redirect_field_name=None, login_url='login')
def change_password(request):
    if request.method == "POST":
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Updating the password logs out all other sessions for the user
            # except the current one.
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/accounts/profile')
    else:
        form = SetPasswordForm(user=request.user)

    return render(
        request, 'accounts/change_password.html', {'form': form}
    )
