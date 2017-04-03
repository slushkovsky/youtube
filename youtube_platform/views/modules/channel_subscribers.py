from django.shortcuts import render

from ...yt_api import query_maker
from .utils import create_social_bases


def channel_subscribers(request, context):
    if request.method == 'POST':
        channel_link = request.POST['channel_link']
        if channel_link.startswith('http'):
            channel = query_maker.query_channel_by_url(channel_link)
        else:
            channel = query_maker.query_channel(channel_link)

        if channel is not None:
            context['result']['details']['channel'] = channel

            sub_channels = query_maker.query_subscribers_from_channel_id(
                channel['channelId']
            )
            res = query_maker.query_socials_by_channel_ids(sub_channels)

            dbs = create_social_bases(res)

            if len(dbs) > 0:
                context['result']['status'] = True
                context['result']['details']['dbs'] = dbs
            else:
                context['result']['status'] = True
                context['result']['errors'] += [
                    'Данный канал не имеет подписчиков'
                ]
        else:
            context['result']['status'] = False
            context['result']['errors'] += ['Канал не найден']

    return render(
        request, 'modules/channel_subscribers.html', context
    )
