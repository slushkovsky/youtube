from googleapiclient.errors import HttpError
from youtube_api.search.youtube_requests import  get_all_playlist_item_links, get_all_subs_links
from youtube_api.search.youtube import  get_channel_id, get_video_id, get_favorites, get_social_links
from youtube_api.search.search import iterate_request_pages
from functools import partial
import isodate

def get_channel_info(youtube, link, get_relatedPlaylists=False):
    # Getting from the link channel_id and validate it
    channel_id = get_channel_id(link, youtube)

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

    socials = get_social_links(
        'https://www.youtube.com/channel/' + channel_id + '/about'
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
    
    result['videoId'] = video_id
    result['title'] = res['items'][0]['snippet']['title']
    result['description'] = res['items'][0]['snippet']['description']
    result['thumbnails'] = res['items'][0]['snippet']['thumbnails']
    result['approved'] = res['items'][0]['contentDetails']['licensedContent']
    result['license'] = res['items'][0]['status']['license']
    result['publishedAt'] = isodate.parse_datetime(
        res['items'][0]['snippet']['publishedAt']
    ).timestamp()
    result['tags'] = res['items'][0]['snippet']['tags']
    result['categoryId'] = res['items'][0]['snippet']['categoryId']
    result['likeCount'] = int(res['items'][0]['statistics']['likeCount'])
    result['dislikeCount'] = int(res['items'][0]['statistics']['dislikeCount'])
    if float(result['likeCount']) + float(result['dislikeCount']) != 0:
        result['likeRate'] = float(result['likeCount']) / (
            float(result['likeCount']) + float(result['dislikeCount'])
        )
    else:
        result['likeRate'] = 0
    result['viewCount'] = int(res['items'][0]['statistics']['viewCount'])
    result['duration'] = isodate.parse_duration(res['items'][0]['contentDetails']['duration']).seconds
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