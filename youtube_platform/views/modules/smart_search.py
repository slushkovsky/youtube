from django.shortcuts import render

from youtube_platform.service_permission import ServicePermission
from .utils import grouper
from ...yt_api import query_maker


permissions = dict(
    subscribers_more_then=ServicePermission.base,
    views_count=ServicePermission.base,
    likes_rate=ServicePermission.standart,
    duration=ServicePermission.standart,
    comments_more_then=ServicePermission.premium,
    upload_earle_then=ServicePermission.premium,
    exclude_approved_channels=ServicePermission.premium,
    cc_license=ServicePermission.premium
)

smart_search_validator = dict(
    key_phase=str, 
    views_policy=str, views_value=int,
    subscribers_policy=str, subscribers_value=int,
    comments_policy=str, comments_value=int, 
    likes_policy=str, likes_value=int,
	duration_policy=str, duration_value=int,
    published_in_policy=str, published_in_value=int,
    exclude_approved_channels=bool,
    cc_license=bool
)


def validate_post_request(user, data):
    res = {}
    errors = []
    for key, value in data.items():
        if key not in smart_search_validator:
            errors += [f'Unexpected key {key}']
            continue

#        if key != 'key_phase':
#            if not user.profile.has_perm(permissions[key]):
#                errors += [f'Have no access to this filter {key}']
#                continue
        if value != '0':
            validator = smart_search_validator[key]
            try:
                res[key] = validator(value)
            except ValueError:
                errors += [
                    f'Expected type {type(validator)} on key {key}'
                ]
    return res, errors


def smart_search(request, context):
    context['permissions'] = {
        k: request.user.profile.has_perm(p)
        for k, p in permissions.items()
    }
    if request.method == 'POST':
        validated, errors = validate_post_request(
            request.user, request.POST
        )
        videos = query_maker.query_smart_search(
            **validated
        )
     
        videos=[1, 2, 3]

        context['result']['errors'] = errors
        context['result']['status'] = True

        context['result']['details'] = list(grouper(videos, 3))

    return render(request, 'modules/smart_search.html', context)
