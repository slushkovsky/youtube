from youtube_platform.service_permission import ServicePermission
from .broadcast_message import broadcast_message
from .channel_dynamic import channel_dynamic
from .channel_subscribers import channel_subscribers
from .collaboration import collaboration
from .count_roi import count_roi
from .popular_tags import popular_tags
from .smart_search import smart_search
from .top3_among_users import top3_among_users
from .top3_video import top3_video
from .user_channels import users_channels
from .video_commentators import video_commentators
from .videos_by_description import videos_by_description


FEATURE_HANDLERS = {
    'users_channels': users_channels,
}

FEATURES = {
    'smart_search': (ServicePermission.base, smart_search),

    'commentators': (ServicePermission.base, video_commentators),
    'user_channels': (ServicePermission.base, users_channels),
    'channel_dynamic': (ServicePermission.base, channel_dynamic),

    'top3_among_users': (ServicePermission.standart, top3_among_users),
    'top3_video': (ServicePermission.standart, top3_video),
    'collaboration': (ServicePermission.standart, collaboration),
    'auditory_analyze': ServicePermission.standart,
    'popular_tags': (ServicePermission.standart, popular_tags),

    'channel_subscribers': (ServicePermission.premium, channel_subscribers),
    'foreign_ad_track': (ServicePermission.premium, videos_by_description),
    'broadcast_message': (ServicePermission.premium, broadcast_message),
    'count_roi': (ServicePermission.premium, count_roi)
}
