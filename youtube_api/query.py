from collections import defaultdict, Counter
from itertools import groupby
from re import compile
import operator


class YtPlatformQuery(object):
    def __init__(self, mongo_db):
        self._mongo_db = mongo_db
        self._videos_collection = mongo_db.get_collection('yt_local_videos')
        self._channels_collection = mongo_db.get_collection('yt_local_channels')
        self._playlists_collection = mongo_db.get_collection('yt_local_playlists')
        self._likes_collection = mongo_db.get_collection('yt_likes')
        self._subscriptions_collection = mongo_db.get_collection('yt_subscriptions')
        self._statistic_collection = mongo_db.get_collection('yt_statistic')
        self._tags_collection = mongo_db.get_collection('yt_tags')
        self._popular_tags_collection = mongo_db.get_collection('yt_popular_tags')

    def query_channels_audithory(self, channels_ids, top_count=5):
        all_subs = []
        all_categories = []

        for channel_id in channels_ids: 
            subs_list = self._channels_collection.find({'channelId': channel_id})[0].get("subsLink")  
            if subs_list is not None: 
                all_subs += [sub["channelUrl"] for sub in subs_list]
 
            videos_list = self._videos_collection.find({'channelId': channel_id})

            for video in videos_list: 
                all_categories.append(video.get('categoryId'))

        subs_counts = Counter(all_subs)
        categories_counts = Counter(all_categories)

        top_subs = sorted(subs_counts.items(), key=operator.itemgetter(1))[-top_count:]
        top_categories = sorted(categories_counts.items(), key=operator.itemgetter(1))[-top_count:]

        return {
            'channels': [sub[0] for sub in top_subs], 
            'categories': [cat[0] for cat in top_categories]
        }

             
    def query_users_channels(self, social_name, social_links):
        return [
            {
                'social_link': sl,
                'channel':
                    [res.get('channelId') for res in list(
                        self._channels_collection.find(
                            {f'socials.{social_name}': sl}
                        )
                    )]
            } for sl in social_links
        ]


    def query_most_liked_among_channels(self, channel_ids, top_count=3):
        channels = self._channels_collection.find({'channelId': {'$in': channel_ids}}) 

        all_liked = []        
 
        for channel in channels: 
            liked = channel.get('likePlaylist', [])

            if liked is None: 
                liked = []
   
            all_liked += liked 

        liked_counts = Counter(all_liked) 

        top = sorted(liked_counts.items(), key=operator.itemgetter(1))[-top_count:]

        return [video[0] for video in top]

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

    def query_video_likes(self, video_url):
        return self._channels_collection.find({'likePlaylist': {'$in': [video_url.split('=')[-1]]}})

    def query_top_video(self, limit=None):
        q = self._videos_collection.find().sort(
            [('viewCount', -1), ('likeCount', -1), ('commentCount', -1)]
        )
        if limit is not None:
            q = q.limit(limit)
        return list(q)

    def query_channel_statistic(self, channel_id):
        return list(self._channels_collection.find(
            {'channelId': channel_id}
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
        return video['commentAuthors']

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
        tags = {}
        for obj in self._videos_collection.find():
            for tag in obj['tags']:
                tags[tag] = tags.get(tag, 0) + 1
      
        import operator
        sorted_tags = sorted(tags.items(), key=operator.itemgetter(1))

        if limit is not None: 
            return sorted_tags[-limit:]
        return sorted_tags

    def query_video_by_description(self, description):
        return list(self._videos_collection.find(
            {'description': description}
        ).limit(100))

    def query_smart_search(
        self, category=None, key_phase=None, subscribers_policy=None, subscribers_value=None, views_policy=None, views_value=None, 
        likes_policy=None, likes_value=None, duration_policy=None, duration_value=None, comments_policy=None, comments_value=None, 
        published_in_policy=None, published_in_value=None, exclude_approved_channels=None, cc_license=None
    ):
        conditions = []

        policy_to_mongo_operator = lambda policy: '$gt' if policy == 'more' else '$lt'

        if key_phase is not None:
            conditions.append(
                {'title': compile(r'.*{}.*'.format(key_phase))}
            )
        if subscribers_policy is not None and subscribers_value is not None:
            conditions.append(
                {'channel.statistic.subscriberCount': {policy_to_mongo_operator(subscribers_policy): subscribers_value}}
            )
        if views_policy is not None and views_value is not None:
            conditions.append(
                {'viewCount': {policy_to_mongo_operator(views_policy): views_value}}
            )
        if likes_policy is not None and likes_value is not None:
            conditions.append(
                {'likeRate': {policy_to_mongo_operator(likes_policy): likes_value}}
            )
        if duration_policy is not None and duration_value is not None:
            conditions.append(
                {'duration': {policy_to_mongo_operator(duration_policy): duration_value}}
            )
        if comments_policy is not None and comments_value is not None:
            conditions.append(
                {'commentsCount': {policy_to_mongo_operator(comments_policy): comments_value}}
            )
        if published_in_policy is not None and published_in_value:
            conditions.append(
                {'publishedAt': {policy_to_mongo_operator(published_in_policy): published_in_value}}
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
