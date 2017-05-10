import re
from math import ceil

from django.shortcuts import render
from django.forms import Form, FileField  

from ...yt_api import query_maker


CHANNEL_LINK_RE = re.compile(
    r'https?://www.youtube.com/channel/(.*)/?'
)


class UCForm(Form):
    links = FileField()

def auditory_analyze(request, context, channel_link=None):
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
 
            top = query_maker.query_channels_audithory(channel_ids)
   
            context['result']['status'] = True
            context['result']['details'] = top   

    return render(
        request, 'modules/auditory_analyze.html', context
    )
