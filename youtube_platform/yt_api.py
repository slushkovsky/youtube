from youtube_api.query import YtPlatformQuery
from youtube_api.discoverer.discoverer import Discoverer
from youtube_api.message_broadcast.message_broadcast import MessageBroadcaster
from youtube_api.search.youtube import build_youtube

from .mongo import mongo_db


youtube = build_youtube()
query_maker = YtPlatformQuery(mongo_db)
discoverer = Discoverer(youtube, mongo_db)


def _create_selenium():
    from django.conf import settings
    import importlib

    sel_cong = settings.SELENIUM
    driver_module_name, driver_class_name = sel_cong['DRIVER_NAME'].rsplit(
        '.', 1
    )
    module = importlib.import_module(driver_module_name)
    driver_class = getattr(module, driver_class_name)

    return driver_class(*sel_cong['DRIVER_ARGS'])


def message_broadcaster_factory() -> MessageBroadcaster:
    from django.conf import settings
    from threading import current_thread

    ct = current_thread()
    if not hasattr(ct, '_message_broadcaster'):
        broadcaster_conf = settings.MESSAGE_BROADCASTER
        setattr(
            ct, '_message_broadcaster', MessageBroadcaster(
                _create_selenium(),
                broadcaster_conf['login'], broadcaster_conf['password']
            )
        )
    return getattr(ct, '_message_broadcaster')
