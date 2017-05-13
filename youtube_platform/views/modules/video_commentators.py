from django.shortcuts import render

from ...yt_api import query_maker
from .utils import create_social_bases


def video_commentators(request, context):
    if request.method == 'POST':
        video_link = request.POST['video_link']
        if not video_link.startswith('http'):
            video = query_maker.query_video(video_link)
        else:
            video = query_maker.query_video_by_url(video_link)

        if video is not None:
            context['result']['details']['video'] = video

            c = query_maker.query_commentators_from_video_id(
                video['videoId']
			)

            res = query_maker.query_socials_by_channel_ids(
                c
            )

            dbs = create_social_bases(res)

            if len(c) > 0:
                context['result']['status'] = True
                context['result']['details']['channels'] = c   

                if len(dbs) > 0: 
                    context['result']['details']['dbs'] = dbs
            else:
                context['result']['status'] = True
                context['result']['errors'] += [
                    'Данное видео никто не комментировал'
                ]
        else:
            context['result']['status'] = False
            context['result']['errors'] += ['Видео не найдено']

    return render(
        request, 'modules/commentators.html', context
    )
