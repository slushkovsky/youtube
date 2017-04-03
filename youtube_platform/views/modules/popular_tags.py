from itertools import count

from django.shortcuts import render

from ...yt_api import query_maker


def popular_tags(request, context):
    tags = query_maker.query_popular_tags(100)

    context['result']['details'] = [
        {
            'place': p,
            'tag': t['tag'],
            'mentionCount': t['mentionCount']
        }
        for p, t in zip(count(1), tags)
    ]
    context['result']['status'] = True

    return render(request, 'modules/popular_tags.html', context)
