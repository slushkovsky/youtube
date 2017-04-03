from django.contrib.auth.decorators import login_required

from youtube_platform.service_permission import ServicePermission
from .entry_point import entry_point


@login_required
def handle_index(request):
    if request.user.profile.has_perm(ServicePermission.standart):
        return entry_point(request, 'top3_video')
    else:
        return entry_point(
            request, 'channel_dynamic',
            channel_link=request.user.profile.channel_url
        )
