from django.shortcuts import render

from ...yt_api import query_maker


def collaboration(request, context):
    self_channel_id = request.user.profile.channel_id
    self_channel = query_maker.query_channel_by_url(
        request.user.profile.channel_url
    )
    if self_channel is None:
        context['result']['status'] = False
        context['result']['errors'].append('Не удаётся получить информацию о ' \
                            'вашем канале. Пожалуйста, повторите ' \
                            'попытку позже.')
    else:
        context['self_channel'] = self_channel
        if self_channel_id is None or len(self_channel_id) == 0:
            self_channel_id = self_channel['channelId']

        if self_channel_id is not None:
            collaborators = query_maker.query_collaborators(
                self_channel_id
            )
            context['result']['status'] = True
            context['result']['details'] = collaborators

    return render(request, 'modules/collaboration.html', context)
