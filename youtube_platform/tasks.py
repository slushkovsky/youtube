from celery import shared_task
from .yt_api import discoverer, message_broadcaster_factory


@shared_task
def explore_youtube(region=None):
    if region is None:
        region = 'RU'

    discoverer.find_categories_by_region(region)


@shared_task
def broadcast_message_task(task_id, recipients, message):
    from .models import MessageBroadcastTask
    message_task = MessageBroadcastTask.objects.filter(id=task_id)

    broadcaster = message_broadcaster_factory()
    try:
        broadcaster.do_login()
        broadcaster.broadcast_message(
            recipients, message
        )
    except Exception:
        message_task.success = False
        message_task.done = True
    else:
        message_task.success = True
        message_task.done = True
    finally:
        message_task.save()
