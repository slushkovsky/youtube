from functools import lru_cache

from django.shortcuts import render
from django.forms import forms, fields


from ...yt_api import query_maker


class MessageForm(forms.Form):
    channels = fields.CharField()
    message = fields.CharField()


@lru_cache(maxsize=512)
def _get_channel(channel_url):
    return query_maker.query_channel_by_url(
        channel_url
    )


def broadcast_message(request, context):
    from ...models import MessageBroadcastTask
    from ...tasks import broadcast_message_task

    form = MessageForm(request.POST)
    context['form'] = form

    context['messages'] = [
        {
            'message': m.message,
            'recipients': [
                channel if channel is not None else r
                for channel, r in (
                    (_get_channel(r), r)
                    for r in m.recipients.split(';')
                )
            ],
            'status': 'success' if m.done and m.success else 'pending',
            'datetime': m.datetime
        }
        for m in MessageBroadcastTask.objects.filter(
            user=request.user.profile
        )[:50]
    ]

    if request.method == 'POST':
        if not form.is_valid():
            context['errors'] += ['Неправильный ввод']
        else:
            channels = [
                p.strip()
                for p in request.POST['channels'].splitlines()
            ]
            message = request.POST['message']

            profile = request.user.profile
            message_task = MessageBroadcastTask.objects.create(
                user=profile, recipients=';'.join(channels),
                message=message, done=False, success=False
            )

            broadcast_message_task.delay(
                message_task.id, channels, message
            )

            context['result']['status'] = True

    return render(request, 'modules/broadcast_message.html', context)
