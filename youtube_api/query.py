from collections import defaultdict
from itertools import groupby
from re import compile


class YtPlatformQuery(object):
    def __init__(self, mongo_db):
        self._mongo_db = mongo_db
        self._videos_collection = mongo_db.get_collection('yt_videos')
        self._channels_collection = mongo_db.get_collection('yt_channels')
        self._playlists_collection = mongo_db.get_collection('yt_playlists')
        self._likes_collection = mongo_db.get_collection('yt_likes')
        self._subscriptions_collection = mongo_db.get_collection('yt_subscriptions')
        self._statistic_collection = mongo_db.get_collection('yt_statistic')
        self._tags_collection = mongo_db.get_collection('yt_tags')
        self._popular_tags_collection = mongo_db.get_collection('yt_popular_tags')

    def query_users_channels(self, social_name, social_links):
        return [
            {
                'social_link': sl,
                'channel':
                    list(
                        self._channels_collection.find(
                            {f'channelInfo.socials.{social_name}': sl},
                            {'channelId': 1, 'channelUrl': 1}
                        )
                    )
            } for sl in social_links
        ]

    def query_most_liked_among_channels(self, channel_ids):
        likes = self._likes_collection.find(
            {'channelId': {'$in': channel_ids}}
        )
        likes_per_video = defaultdict(int)
        for l in likes:
            likes_per_video[l['videoId']] += 1

        likes_per_channel = defaultdict(list)
        for l in likes:
            likes_per_channel[l['channelId']].append(l['videoId'])

        common_video = set().intersection(*likes_per_channel.values())

        return sorted(list(common_video))

    def query_channel(self, channel_id):
        return self._channels_collection.find_one(
            {'channelId': channel_id}
        )

    def query_channel_by_url(self, channel_url):
        return self._channels_collection.find_one(
            {'channelUrl': channel_url}
        )

    def query_video(self, video_id):
        return self._videos_collection.find_one(
            {'videoId': video_id}
        )

    def query_video_by_url(self, video_url):
        return self._videos_collection.find_one(
            {'videoUrl': video_url}
        )

    def query_top_video(self, limit=None):
        q = self._videos_collection.find().sort(
            [('viewCount', -1), ('likeCount', -1), ('commentCount', -1)]
        )
        if limit is not None:
            q = q.limit(limit)
        return list(q)

    def query_channel_statistic(self, channel_id):
        return list(self._statistic_collection.find(
            {'channelId': channel_id},
            {'statistics': 1, 'datetime': 1}
        ))

    def query_collaborators(self, channel_id):
        subscribers = self._subscriptions_collection.find(
            {'subChannelId': channel_id}
        )
        subscriptions = self._subscriptions_collection.find(
            {
                'channelId': {'$in': [s['channelId'] for s in subscribers]},
                'subChannelId': {'$ne': channel_id}
            }
        ).sort([('subChannelId', 1)])
        groupped = groupby(subscriptions, lambda s: s['subChannelId'])
        groupped = [
            (sub, len(subs)) for sub, subs in groupped
        ]
        groupped.sort(key=lambda v: v[1])
        return groupped

    def query_commentators_from_video_id(self, video_id):
        video = self._videos_collection.find(
            {'videoId': video_id}
        )
        if video.count == 0:
            return []
        video = video[0]
        return [
            {
                'authorChannelUrl': c['authorChannelUrl'],
                'authorChannelId': c['authorChannelId'],
            }
            for c in video['comments']
        ]

    def query_likers_from_video_id(self, video_id):
        likers = self._likes_collection.find(
            {'videoId': video_id}, {'channelId': 1}
        )
        return likers

    def query_subscribers_form_video(self, video_id):
        video = self._videos_collection.find(
            {'videoId': video_id}
        )
        if video.count == 0:
            return []
        video = video[0]
        return self.query_subscribers_from_channel_id(video['channelId'])

    def query_subscribers_from_channel_id(self, channel_id):
        return [
            s['channelId']
            for s in self._subscriptions_collection.find(
                {'subChannelId': channel_id}
            )
        ]

    def query_socials_by_channel_ids(self, channel_ids):
        return [
            channel
            for channel in (
                self._channels_collection.find_one(
                    {'channelId': cid},
                    {'channelId': 1, 'channelUrl': 1, 'channelInfo.socials': 1}
                )
                for cid in channel_ids
            )
            if channel is not None
        ]

    def query_popular_tags(self, limit=None):
        q = self._popular_tags_collection.find().sort(
            [('mentionCount', -1)]
        )
        if limit is not None:
            q = q.limit(limit)
        return list(q)

    def query_video_by_description(self, description):
        return list(self._videos_collection.find(
            {'description': description}
        ).limit(100))

    def query_smart_search(
        self, category=None, key_phase=None, subscribers_more_then=None, views_count=None,
        likes_rate=None, duration=None, comments_more_then=None, upload_earle_then=None,
        exclude_approved_channels=None, cc_license=None
    ):
        conditions = []
        if key_phase is not None:
            conditions.append(
                {'title': compile(r'.*{}.*'.format(key_phase))}
            )
        if subscribers_more_then is not None:
            conditions.append(
                {'channel.statistic.subscriberCount': {'$gt': subscribers_more_then}}
            )
        if views_count is not None:
            conditions.append(
                {'viewCount': {'$gt': views_count}}
            )
        if likes_rate is not None:
            conditions.append(
                {'likeRate': {'$gt': likes_rate}}
            )
        if duration is not None:
            conditions.append(
                {'duration': {'$gt': duration}}
            )
        if comments_more_then is not None:
            conditions.append(
                {'commentsCount': {'$gt': comments_more_then}}
            )
        if upload_earle_then is not None:
            conditions.append(
                {'publishedAt': {'$lt': upload_earle_then}}
            )
        if exclude_approved_channels:
            conditions.append(
                {'approved': False}
            )
        if cc_license:
            conditions.append(
                {'license': 'creativeCommon'}
            )
        and_condition = {}
        for c in conditions:
            and_condition.update(c)

        t = self._videos_collection.aggregate([
            {
                '$lookup': {
                    'from': 'yt_channels',
                    'localField': 'channelId',
                    'foreignField': 'channelId',
                    'as': 'channel'
                }
            },
            {
                '$match': and_condition
            },
            {
                '$limit': 100
            }
        ])

        return list(t)
