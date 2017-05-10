from itertools import count

from django.shortcuts import render

from ...yt_api import query_maker


def popular_tags(request, context):
    tags = query_maker.query_popular_tags(10)

    tags = tags[::-1]

    context['result']['details'] = [
        {
            'tag': tag,
            'mentionCount': count
        }
        for tag, count in tags
    ]
    context['result']['status'] = True

    return render(request, 'modules/popular_tags.html', context)
