import re
from math import ceil

from django.shortcuts import render

from ...yt_api import query_maker


CHANNEL_LINK_RE = re.compile(
    r'https?://www.youtube.com/channel/(.*)/?'
)


def auditory_analyze(request, context, channel_link=None):
    if request.method == 'POST' or channel_link is not None:
        channel_link = request.POST.get('channel_link') or channel_link

        match = CHANNEL_LINK_RE.match(channel_link)
        if match is not None:
            channel_id = match.groups()[0]
        else:
            channel_id = channel_link

        res = query_maker.query_channel_statistic(channel_id)
        channel = query_maker.query_channel(channel_id)
        if len(res) > 0:
            grow = [1]
            for m_prev, m in zip(res, res[1:]):
                m_prev_stat = m_prev['statistics']
                m_stat = m['statistics']
                c = s = v = l = d = 0
                if m_prev_stat['commentCount'] > 0:
                    c = m_stat['commentCount'] / m_prev_stat['commentCount']
                if m_prev_stat['subscriberCount'] > 0:
                    s = m_stat['subscriberCount'] / m_prev_stat['subscriberCount']
                if m_prev_stat['viewCount'] > 0:
                    v = m_stat['viewCount'] / m_prev_stat['viewCount']
                if m_prev_stat['likeCount'] > 0:
                    l = m_stat['likeCount'] / m_prev_stat['likeCount']
                if m_prev_stat['dislikeRate'] > 0:
                    d = m_stat['dislikeRate'] / m_prev_stat['dislikeRate']
                grow.append((c + s + v + (l + d)/2) / 4)

            context['result']['details'] = {}
            context['result']['details']['channel'] = channel
            context['result']['details']['statistics'] = [
                {
                    'datetime': m['datetime'].isoformat(),
                    'comments': m['statistics']['commentCount'],
                    'subscribers': m['statistics']['subscriberCount'],
                    'likes': m['statistics']['likeCount'],
                    'views': m['statistics']['viewCount'],
                    'grow': g
                } for m, g in zip(res, grow)
            ]
            if channel['statistics']['likeCount'] + channel['statistics']['dislikeCount'] > 0:
                context['result']['details']['dislikeRate'] = ceil((
                    float(channel['statistics']['dislikeCount']) / (
                        channel['statistics']['likeCount'] +
                        channel['statistics']['dislikeCount']
                    )
                ) * 100)
            else:
                context['result']['details']['statistics']['dislikeRate'] = 0
            context['result']['status'] = True
        else:
            context['result']['status'] = False
            context['result']['errors'] = ['Канал не найден']

    return render(
        request, 'modules/auditory_analyze.html', context
    )
