# -*- coding: utf-8 -*-


from youtube_api.search.youtube_requests import  get_all_playlists_links, get_all_playlist_item_links
from youtube_api.search.youtube import  build_youtube, get_playlist_link
#from youtube_api.search.statistics import  
from hotfix import get_channel_info, get_comment_list_statistics, get_video_statistics, get_video_categories, list_most_popular_videos
from pymongo import MongoClient

import sys

COLNAME_PREFIX = 'yt_local_'

# YtLocalStore #

class YtLocalStore(object):
    def __init__(self, mongo_db, **kw):
        self._mongo_db = mongo_db
        # Options (kw):
            # continue - если нужно продолжить с последней неудачной попытки, по умолчанию False
            # max_memory - предел по объему памяти данных [Mb], по умолчанию 0
            # max_channels - предел по количеству обработанных каналов, по умолчанию 0
            # max_videos - предел по количеству обработанных видео, по умолчанию 0
        self.opts = kw
        # Статистика обработки
        self.szMemory = self.nChannels = self.nVideos = 0  
        
        self._channels_src = mongo_db.get_collection('yt_channels')
        #self._videos_src = mongo_db.get_collection('yt_videos')
        
        self._videos_collection = mongo_db.get_collection(COLNAME_PREFIX + 'videos')
        self._channels_collection = mongo_db.get_collection(COLNAME_PREFIX + 'channels')
        self._comments_collection = mongo_db.get_collection(COLNAME_PREFIX + 'comments')
        
        #self._playlists_collection = mongo_db.get_collection(COLNAME_PREFIX + 'playlists')
        #self._likes_collection = mongo_db.get_collection(COLNAME_PREFIX + 'likes')
        #self._subscriptions_collection = mongo_db.get_collection(COLNAME_PREFIX + 'subscriptions')
        #self._statistic_collection = mongo_db.get_collection(COLNAME_PREFIX + 'statistic')
        #self._tags_collection = mongo_db.get_collection(COLNAME_PREFIX + 'tags')
        
    def getChannelList(self):
         # Продолжить или начать заново?
        shouldContinue = self.opts.get('continue', False)
        if  shouldContinue:
            n = self._channels_collection.count() #processed count + last interrupted
            uChannelList = self._channels_src.find().distinct("channelId")
            return uChannelList[n-1:] #sliced list
        
         # Очистить старые записи из 'channels_src'
        self._channels_src.remove({})
        # Уникальный индекс для строковых ключей не работает
        #self._channels_src.create_index('channelId', unique=True)
        
        categories = get_video_categories(self.yt)
        for catId, title in  categories:
            #print(( "Category: %s "%catId).center(40, '='))
            videoItems = list_most_popular_videos(self.yt, catId)
            """
            for i, videoItem in enumerate(videoItems):
                print("ITEM:%3d"%i, videoItem)
                #print('='*40)
                #print("{0:<16} {1}".format(videoItem['videoId'], videoItem['channelId']))
            if int(catId) == 18:
                break
            input()
         """
            if videoItems:
                self._channels_src.insert_many(videoItems)
         # Вернуть итератор по уникальным значениям
        print("Total channels found:",self._channels_src.count())
        return self._channels_src.find().distinct("channelId")
             
    def update(self):
        self.yt = build_youtube()
        shouldContinue = self.opts.get('continue', False)
        if not shouldContinue:
            # Очистить старые записи из 'channels'
            self._channels_collection.remove({})
            # Очистить старые записи из 'videos'
            self._videos_collection.remove({})
            # Очистить старые записи из 'comments'
            self._comments_collection.remove({})
        
        max_memory = self.opts.get('max_memory', 0) << 20 #to bytes
        max_channels = self.opts.get('max_channels', 0)
        max_videos = self.opts.get('max_videos', 0)
        
        #for channel in self._channels_src.find():
        for channel_id in self.getChannelList():            
            # Получаем:
            # - Список ссылок плейлисты канала                  : playlists
            plist_ids = get_all_playlists_links(self.yt, channel_id)
            # Получаем:
            # - Ссылки на соц. сети                             : socials
            # - Список понравившихся видео                      : likePlaylist
            # - Список favorites видео                          : favoritesLink
            # - Название канала                                 : channelTitle
            # - Описание канала                                 : channelDescription
            # - Список подписок канала (на кого он подписан)    : subsLink
            # - URL иконки канала                               : thumbnails
            info = get_channel_info(self.yt, channel_id, get_relatedPlaylists=True)
            channelInfo = info['channelInfo']
            #statistics = info['statistics']
            #channelInfo['statistics'] =  statistics
            # NOTE: Нет смысла сохранять плейлисты ссылками, достаточно только айди, так как ссылки легко получаются путем прибавления префикса к айди.
            channelInfo['playlists'] =  plist_ids #[get_playlist_link(plist_id ) for plist_id in plist_ids]
            channelInfo['channelId'] =  channel_id 
            if not shouldContinue:
                self._channels_collection.insert_one(channelInfo)
                self.nChannels += 1
                self.szMemory += sys.getsizeof(channelInfo)
            else:
                input("Continue from channel: `%s`. Press any key..." % channel_id)
            
            # Собрать статистику по каждому видео из 'uploads' (все видео, принадлежащих каналу)
            plist_uploads = info['relatedPlaylists']['uploads']
            uploaded_vids = get_all_playlist_item_links(self.yt, plist_uploads)
            if shouldContinue:
                # Определить необработанные еще видео из списка uploaded_vids. Пропустить те, которые уже находятся в БД 
                uploaded_vids = self.getUnprocessedVideoList(channel_id, uploaded_vids)
                input("Continue from video: `%s`. Press any key..." % uploaded_vids[0])
                shouldContinue = False
            for vid in uploaded_vids:
                # Получаем:
                # - Кол-во лайков/дислайков под видео                                   : likeCount/dislikeCount
                # - Название видео                                                      : title
                # - Описание видео                                                      : description            
                # - Ссылка на миниатюру видео                                           : thumbnails
                # - Время публикации                                                    : publishedAt    
                # - Категория                                                           : categoryId    
                # - Теги                                                                : tags
                # - Длина                                                               : duration    
                # - Кол-во просмотров                                                   : viewCount
                videoInfo = get_video_statistics(self.yt, vid)
                if not videoInfo:
                    # NOTE: Если информация по видео не полная, пропустить. Пример такого видео: `XODqm66ooMQ`
                    print("Skip bad video:", vid, 'channel:', channel_id)
                    continue
                # - Список пользователей, оставивших комментарий                        : commentAuthors
                # - Кол-во комментариев                                                 : commentsCount
                # - Список комментариев (для каждого: текст, ссылка на автора, рейтинг)   : отдельная коллекция 'comments'
                comments = get_comment_list_statistics(self.yt, vid)
                authors = self.getCommentAuthors(comments)
                videoInfo['commentAuthors'] = authors
                videoInfo['commentsCount'] = len(comments)
                # - Ссылка на плейлисты, в которых находится видео (все плейлисты, кроме plist_uploads или только он и нужен?)
                # NOTE: Чтобы определить все плейлисты, в которых находится видео, достаточно выполнить запрос к БД. Поэтому плелист один
                container_plist_ids = [plist_uploads] #+ self.getPlaylistIdsThatVideoBelongsTo(vid)
                videoInfo['playlists'] =  [get_playlist_link(plist_id ) for plist_id in container_plist_ids]
                # Ключ канала
                videoInfo['channelId'] = channel_id
                # Сохранить видео
                self._videos_collection.insert_one(videoInfo)
                self.nVideos += 1
                self.szMemory += sys.getsizeof(videoInfo)
                if max_videos > 0 and self.nVideos > max_videos:
                    return
                # Сохранить 'comments'
                if comments:
                    self._comments_collection.insert_many(comments)
                    self.szMemory += sys.getsizeof(comments)
                    
            if max_channels > 0 and self.nChannels > max_channels:
                return
            if max_memory > 0 and self.szMemory > max_memory:
                return
                
    def getUnprocessedVideoList(self, channelId, uploaded_vids):
        savedItems = [i['videoId'] for i in self._videos_collection.find({'channelId':channelId}, {'videoId':1})]
        # Get the difference. Preserve order of `uploaded_vids`
        visited = set(savedItems)
        unvisited = [i for i in uploaded_vids if i not in visited]
        return unvisited
    
    def loadPlaylistsVideoIds(self, plist_ids):
        self.videos_map = {}
        for  plist in plist_ids:
            vids = get_all_playlist_item_links(self.yt, plist)
            self.videos_map[plist] = vids
        
    def getPlaylistIdsThatVideoBelongsTo(self, video_id):
        # Поиск плейлистов, в которых находится данное видео
        plist_ids = []
        for plist_id in self.videos_map:
            if video_id in self.videos_map[plist_id]:
                plist_ids.append(plist_id)
        return plist_ids
        
    def getCommentAuthors(self, comments):
        u_authors = set()
        authors = []
        for c in comments:
            if c['authorChannelId'] not in u_authors:
                authors.append(c['authorChannelUrl'])
                u_authors.add(c['authorChannelId'])
        return authors
    
    def showStats(self):
        print(" Обработано ".center(40, '*'))
        print("Количество каналов:", self.nChannels)
        print("Количество памяти:", self.szMemory)
        print("Количество видео:", self.nVideos)
        
    def getStats(self):
        return {
            "nChannels": self.nChannels,
            "szMemory": self.szMemory,
            "nVideos": self.nVideos
        }

if __name__ == '__main__':
    from sys import stdout, argv
    from logging import getLogger, DEBUG, StreamHandler
    import argparse

    log = getLogger()
    log.setLevel(DEBUG)
    log.addHandler(StreamHandler(stdout))

    parser = argparse.ArgumentParser(description='Обновление данных по Youtube API')
    parser.add_argument('-c', '--continue', help='если нужно продолжить с последней неудачной попытки', action='store_true')
    parser.add_argument('-mm', '--max-memory', help="предел по объему памяти данных [МB]", default=0, type=int)
    parser.add_argument('-mc', '--max-channels', help="предел по количеству обработанных каналов", default=0, type=int)
    parser.add_argument('-mv', '--max-videos', help="предел по количеству обработанных видео", default=0, type=int)
    args = parser.parse_args(sys.argv[1:])
    #print(vars(args))    
    
    client = MongoClient()
    st = YtLocalStore(client.youtube, **vars(args))
    st.update()
    st.showStats()
    
