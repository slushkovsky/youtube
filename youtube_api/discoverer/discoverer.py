import itertools
from functools import partial

import datetime

from ..search.search import get_channel_info, get_playlists_info, get_playlists_video_ids
from ..utils import log


def iterate_request_pages(request_maker):
    res = request_maker().execute()
    yield res

    if 'nextPageToken' in res:
        next_page = res['nextPageToken']
        while True:
            res = request_maker(pageToken=next_page).execute()
            yield res

            if 'nextPageToken' not in res:
                break

            next_page = res['nextPageToken']


class Discoverer(object):
    def __init__(self, yt_api, mongo_db):
        self._yt_api = yt_api
        self._mongo_db = mongo_db
        self._videos_collection = mongo_db.get_collection('yt_videos')
        self._channels_collection = mongo_db.get_collection('yt_channels')
        self._playlists_collection = mongo_db.get_collection('yt_playlists')
        self._likes_collection = mongo_db.get_collection('yt_likes')
        self._subscriptions_collection = mongo_db.get_collection('yt_subscriptions')
        self._statistic_collection = mongo_db.get_collection('yt_statistic')
        self._tags_collection = mongo_db.get_collection('yt_tags')
        self._popular_tags_collection = mongo_db.get_collection('yt_popular_tags')

    def find_categories_by_region(self, code):
        res = self._yt_api.guideCategories.list(part='snippet', regionCode=code)
        self._report_process_region(code)
        for i in res['items']:
            self._report_process_category(i['id'])
            self.find_channels_by_category(i['id'])

    def find_channels_by_category(self, category):
        maker = partial(
            self._yt_api.channels.list, categoryId=category, part='id'
        )
        return itertools.chain.from_iterable(
            (
                (
                    channel['id']
                    for channel in page['items']
                )
                for page in iterate_request_pages(maker)
            )
        )

    def process_channel(self, channel_id):
        log.info(f'Processing channel {channel_id}...')

        self._report_process_channel(channel_id)

        channel_link = 'https://www.youtube.com/channel/{}'.format(channel_id)
        channel_meta = get_channel_info(
            self._yt_api, channel_link
        )

        like_playlist = channel_meta['channelInfo']['likePlaylist']
        if like_playlist is not None:
            self._likes_collection.delete_many({'channelId': channel_id})
            self._likes_collection.insert_many([
                {
                    'channelId': channel_id,
                    'videoId': vid
                }
                for vid in like_playlist
            ])

        subs_links = channel_meta['channelInfo']['subsLink']
        if subs_links is not None:
            self._subscriptions_collection.delete_many({'channelId': channel_id})
            self._subscriptions_collection.insert_many([
                {
                    'channelId': channel_id,
                    'subChannelId': cid['channelId']
                }
                for cid in subs_links
            ])

        playlists_meta = get_playlists_info(self._yt_api, channel_link)
        # channel_meta['playlistsMeta'] = playlists_meta

        channel_meta['statistics']['likeCount'] = sum(
            itertools.chain.from_iterable(
                (v['likeCount'] for v in pl['videoItems'])
                for pl in playlists_meta['playlistsInfo']
            )
        )
        channel_meta['statistics']['dislikeCount'] = sum(
            itertools.chain.from_iterable(
                (v['dislikeCount'] for v in pl['videoItems'])
                for pl in playlists_meta['playlistsInfo']
            )
        )

        self._statistic_collection.insert_one(
            {
                'channelId': channel_id,
                'datetime': datetime.datetime.utcnow(),
                'statistics': channel_meta['statistics']
            }
        )

        videos = itertools.chain.from_iterable([
            [
                dict(channelId=channel_id, **v)
                for v in pl['videoItems']
            ]
            for pl in playlists_meta['playlistsInfo']
        ])

        for video in videos:
            self._videos_collection.update_one(
                {'videoId': video['videoId']},
                {'$set': video}, upsert=True
            )
            for tag in video['tags']:
                if self._tags_collection.find(
                    {'videoId': video['videoId'], 'tag': tag}
                ).count() == 0:
                    self._tags_collection.insert_one(
                        {'videoId': video['videoId'], 'tag': tag}
                    )
                    if self._popular_tags_collection.find(
                        {'tag': tag}
                    ).count() == 0:
                        self._popular_tags_collection.insert_one(
                            {'tag': tag, 'mentionCount': 1}
                        )
                    else:
                        self._popular_tags_collection.update_one(
                            {'videoId': video['videoId'], 'tag': tag},
                            {'$inc': {'mentionCount': 1}}
                        )

        if self._channels_collection.find(
            {'channelId': playlists_meta['channelId']}
        ).count() > 0:
            self._channels_collection.update_one(
                {'channelId': playlists_meta['channelId']},
                {'$set': channel_meta}
            )
        else:
            self._channels_collection.insert_one(channel_meta)

        if self._channels_collection.find(
            {'playlistId': playlists_meta['playlistId']},
        ).count() > 0:
            self._playlists_collection.update_one(
                {'playlistId': playlists_meta['playlistId']},
                {'$set': playlists_meta}
            )
        else:
            self._playlists_collection.insert_one(playlists_meta)

        log.info(f'Processing channel {channel_id} FINISHED')

    def _report_process_region(self, code):
        pass

    def _report_process_category(self, category_id):
        pass

    def _report_process_channel(self, channel_id):
        pass
