from re import compile, IGNORECASE
from django.shortcuts import render

from ...yt_api import query_maker
from .utils import grouper


def videos_by_description(request, context):
    if request.method == 'POST':
        tags = request.POST['tags'].split(',')
        videos = query_maker.query_video_by_description(
            compile(
                r'(?:^|(?<= ))({})(?:(?= )|$)'.format(
                    '|'.join(tags)
                ), flags=IGNORECASE
            )
        )
        print(videos)
        context['result']['status'] = True
        context['result']['details'] = list(grouper(videos, 3))

    return render(request, 'modules/videos_by_description.html', context)
