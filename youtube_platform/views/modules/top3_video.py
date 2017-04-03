from django.shortcuts import render

from ...yt_api import query_maker


def top3_video(request, context):
    context['result']['status'] = True
    context['result']['details'] = [query_maker.query_top_video(3)]

    return render(
        request, 'modules/top3_video.html', context
    )
