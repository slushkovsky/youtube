from googleapiclient.errors import HttpError
from youtube_api.search.youtube_requests import  get_all_playlist_item_links, get_all_subs_links
from youtube_api.search.youtube import  get_channel_id, get_video_id, get_favorites, get_social_links
from youtube_api.search.search import iterate_request_pages
from functools import partial
import isodate

CHANNEL_BASE_URL = "https://www.youtube.com/channel/"

def get_channel_info(youtube, channel_id, get_relatedPlaylists=False):
    # Getting from the link channel_id and validate it
    link = CHANNEL_BASE_URL + channel_id
    #channel_id = get_channel_id(link, youtube)

    # Getting channel parts (snippet, brandingSettings, contentDetails) by id
    channels_list_response = youtube.channels().list(
        id=channel_id,
        part="snippet,statistics,brandingSettings,contentDetails",
        maxResults=20
    ).execute()
    # Getting from response Liked playlist, validate it and making full link
    if 'likes' in channels_list_response['items'][0]['contentDetails']['relatedPlaylists']:
        playlist_id = channels_list_response['items'][0]['contentDetails']['relatedPlaylists']['likes']
        like_playlist = get_all_playlist_item_links(youtube, playlist_id)
    else:
        like_playlist = None

    # Getting from response channel description
    channel_title = channels_list_response['items'][0]['snippet']['localized']['title']
    channel_description = channels_list_response['items'][0]['snippet']['localized']['description']
    # Getting from response channel favorites channels
    # Using custom method!
    favorites_response = get_favorites(channels_list_response)

    # Search subscriptions by channel id
    # Can throws HttpError 403 (accountClosed or accountSuspended or subscriptionForbidden)
    # In this case response = Not allowed
    # Making full subscriptions channels link
    subs_response = get_all_subs_links(youtube, channel_id)

    # NOTE: Этот метода не всегда работает. Например: 
    #       url = 'https://www.youtube.com/channel/UCVYamHliCI9rw1tHR1xbkfw/about'
    #       requests.get(url)
    #       Выдаст: https://www.youtube.com:443 "GET /channel/UCVYamHliCI9rw1tHR1xbkfw/about HTTP/1.1" 200 None
    socials = get_social_links(
        CHANNEL_BASE_URL + channel_id + '/about'
    )
    response = {
        'channelId': channel_id,
        'channelUrl': link,
        'channelInfo': {
            'subsLink': subs_response,
            'favoritesLink': favorites_response,
            'channelTitle': channel_title,
            'channelDescription': channel_description,
            'likePlaylist': like_playlist,
            'socials': socials,
            'thumbnails': channels_list_response['items'][0]['snippet']['thumbnails']
        },
        'statistics': {
            k: int(v)
            for k, v in channels_list_response['items'][0]['statistics'].items()
        }
    }
    
    if get_relatedPlaylists:
        response['relatedPlaylists'] = channels_list_response['items'][0]['contentDetails']['relatedPlaylists']

    return response
    
def get_video_statistics(youtube, video_id):
    result = {}
    res = youtube.videos().list(
        id=video_id,
        part="snippet,statistics,status,contentDetails",
    ).execute()
    
    if not res['items'][0].get('statistics'):
        return
        
    result['videoId'] = video_id
    result['title'] = res['items'][0]['snippet'].get('title', '')
    result['description'] = res['items'][0]['snippet'].get('description', '')
    result['thumbnails'] = res['items'][0]['snippet'].get('thumbnails', '')
    result['approved'] = res['items'][0]['contentDetails'].get('licensedContent', '')
    result['license'] = res['items'][0]['status'].get('license', '')
    result['publishedAt'] = isodate.parse_datetime(
        res['items'][0]['snippet'].get('publishedAt', '')
    ).timestamp()
    result['tags'] = res['items'][0]['snippet'].get('tags', '') #Может отсутствовать (пример видео:XODqm66ooMQ)
    result['categoryId'] = res['items'][0]['snippet'].get('categoryId', '')
    result['likeCount'] = int(res['items'][0]['statistics'].get('likeCount', -1))
    result['dislikeCount'] = int(res['items'][0]['statistics'].get('dislikeCount', -1))
    if float(result['likeCount']) + float(result['dislikeCount']) != 0:
        result['likeRate'] = float(result['likeCount']) / (
            float(result['likeCount']) + float(result['dislikeCount'])
        )
    else:
        result['likeRate'] = 0
    result['viewCount'] = int(res['items'][0]['statistics'].get('viewCount', -1))
    result['duration'] = isodate.parse_duration(res['items'][0]['contentDetails'].get('duration', '2010-08-18 08:15:30Z')).seconds
    result['videoUrl'] = 'https://www.youtube.com/watch?v=' + video_id
    return result
    
def get_comment_list_statistics(youtube, video_id):
    comments = []
    rmaker = partial(
        youtube.commentThreads().list,
        part="snippet,id",
        videoId=video_id,
        maxResults="50",
        order='relevance'
    )
    
    page_iterator = iterate_request_pages(rmaker)
    while True:
        try:
            page = next(page_iterator)
            comments += [get_comment_inst(item, video_id) for item in page['items']]
        except StopIteration:
            break
        except HttpError:
            pass

    return comments
        
def get_comment_inst(item, video_id):
    authorChannelUrl = item['snippet']['topLevelComment']['snippet'].get('authorChannelUrl')
    authorChannelId = item['snippet']['topLevelComment']['snippet'].get('authorChannelId', '')
    authorDisplayName = item['snippet']['topLevelComment']['snippet'].get('authorDisplayName')
    return {
        'commentText': item['snippet']['topLevelComment']['snippet']['textDisplay'],
        'authorChannelUrl': authorChannelUrl,
        'rate': item['snippet']['topLevelComment']['snippet']['likeCount'],
        'authorChannelId': authorChannelId and authorChannelId['value'],
        'authorDisplayName': authorDisplayName,
        'videoId': video_id
    }
    
def get_video_categories(youtube, regionCode='ru'):
    # Getting all categories available for given regiom
    #response = youtube.guideCategories().list(
    response = youtube.videoCategories().list(
        part="snippet",
        regionCode=regionCode
    ).execute()
    
    categories = None
    if response.get('items'):
        categories = [ (item['id'], item.get('snippet') and  item['snippet']['title']) for item in response['items']]
    return categories
    
def get_video_inst(item):
    return {
        'videoId': item['id'],
        'channelId': item['snippet']['channelId']
    }
    
def check_unique(lst, field):
    u = set()
    for item in lst:
        value = item[field]
        if value in u:
            item[field] = '[R] '+value
        else:
            u.add(value)
    
    m = len(u) 
    n = len(lst)
    print('Uniqueness[%s]: %d/%d' % (field, m, n))
    
def list_most_popular_videos(youtube, video_category_id):
    video = []
    rmaker = partial(
        youtube.videos().list,
        part="snippet",
        videoCategoryId=video_category_id,
        maxResults="50",
        chart='mostPopular'
    )
    
    page_iterator = iterate_request_pages(rmaker)
    while True:
        try:
            page = next(page_iterator)
            video += [get_video_inst(item) for item in page['items']]
        except StopIteration:
            break
        except HttpError:
            pass
    
    #check_unique(video, 'videoId')
    #check_unique(video, 'channelId')
    return video
    
