from youtube_api.search.youtube_requests import  get_all_playlists_links, get_all_playlist_item_links
from youtube_api.search.youtube import  build_youtube, get_playlist_link
#from youtube_api.search.statistics import  
from hotfix import get_channel_info, get_comment_list_statistics, get_video_statistics
from pymongo import MongoClient

COLNAME_PREFIX = 'yt_local_'

# YtLocalStore #

class YtLocalStore(object):
    def __init__(self, mongo_db):
        self._mongo_db = mongo_db
    
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
        
    def update(self):
        self.yt = build_youtube(cache_discovery=False)
        # Очистить старые записи из 'channels'
        self._channels_collection.remove({})
        # Очистить старые записи из 'videos'
        self._videos_collection.remove({})
        # Очистить старые записи из 'comments'
        self._comments_collection.remove({})
        
        for channel in self._channels_src.find():
            channel_link = channel['channelUrl']
            channel_id = channel['channelId']
            
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
            info = get_channel_info(self.yt, channel_link, get_relatedPlaylists=True)
            channelInfo = info['channelInfo']
            #statistics = info['statistics']
            #channelInfo['statistics'] =  statistics
            channelInfo['playlists'] =  [get_playlist_link(plist_id ) for plist_id in plist_ids]
            self._channels_collection.insert_one(channelInfo)
        
            # Подготовить список видео для каждого плейлиста (нужно для поиска принадлежности видео к тому или иному плейлисту)
#            self.loadPlaylistsVideoIds(plist_ids)
            # Собрать статистику по каждому видео из 'uploads' (все видео, принадлежащих каналу)
            plist_uploads = info['relatedPlaylists']['uploads']
            uploaded_vids = get_all_playlist_item_links(self.yt, plist_uploads)
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
                # - Список пользователей, оставивших комментарий                        : commentAuthors
                # - Кол-во комментариев                                                 : commentsCount
                # - Список комментариев (для каждого: текст, ссылка на автора, рейтинг)   : отдельная коллекция 'comments'
                comments = get_comment_list_statistics(self.yt, vid)
                authors = self.getCommentAuthors(comments)
                videoInfo['commentAuthors'] = authors
                videoInfo['commentsCount'] = len(comments)
                # - Ссылка на плейлисты, в которых находится видео (все плейлисты, кроме plist_uploads или только он и нужен?)
                container_plist_ids = [plist_uploads] #+ self.getPlaylistIdsThatVideoBelongsTo(vid)
                videoInfo['playlists'] =  [get_playlist_link(plist_id ) for plist_id in container_plist_ids]
                # Ключ канала
                videoInfo['channelId'] = channel_id
                # Сохранить видео
                self._videos_collection.insert_one(videoInfo)
                # Сохранить 'comments'
                if comments:
                    self._comments_collection.insert_many(comments)
                
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
        
if __name__ == '__main__':
    client = MongoClient()
    st = YtLocalStore(client.youtube)
    st.update()
    