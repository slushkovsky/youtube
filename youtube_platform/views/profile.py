from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import FeatureUsage
from ..yt_api import query_maker
from .menu import create_context_from_request


@login_required
def profile(request):
    context = create_context_from_request(request)
    context['disable_page_bg'] = True

    context['user'] = request.user
    context['yt_profile'] = query_maker.query_channel_by_url(
        request.user.profile.channel_url
    )
    context['p_profile'] = request.user.profile
    context['usage_history'] = [
        u.dict()
        for u in FeatureUsage.objects.filter(user=request.user.profile)[:50]
    ]

    return render(request, 'accounts/profile.html', context)
