from django.forms import Form, FileField
from django.shortcuts import render

from ...yt_api import query_maker


class UCForm(Form):
    links = FileField()


def top3_among_users(request, context):
    if request.method == 'POST':
        form = UCForm(request.POST, request.FILES)
        context['form'] = form

        if form.is_valid():
            file = request.FILES['links']
            channel_links = [
                l.decode().strip() for l in file.readlines()
            ]
            channel_ids = [
                cid if isinstance(cid, str) or cid is None else cid['channelId']
                for cid in (
                    link if not link.startswith('http')
                    else query_maker.query_channel_by_url(link)
                    for link in channel_links
                )
            ]
            getattr(request, 'add_to_params')['links'] = channel_links

            print(channel_ids) 

            if len(channel_ids) == 0:
                context['result']['status'] = False
                context['result']['errors'] += ['Список каналов пуст']
            else:
                print(query_maker.query_most_liked_among_channels(channel_ids))

                res = [
                    query_maker.query_video(vid)
                    for vid in query_maker.query_most_liked_among_channels(
                        channel_ids
                    )
                ]

                context['result']['status'] = True
                context['result']['details'] = [res]

    return render(
        request, 'modules/top3_among_users.html', context
    )
