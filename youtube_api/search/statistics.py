from dateutil.parser import parse
from googleapiclient.errors import HttpError
import isodate

from .youtube_requests import get_all_playlist_item_links


def get_playlist_statistics(youtube, playlist_id):
    result = {}

    playlist_items_id = get_all_playlist_item_links(youtube, playlist_id)
    result['playlistUrl'] = 'https://www.youtube.com/playlist?list=' + playlist_id
    result['videoItems'] = [
        get_video_statistics(youtube, item) for item in playlist_items_id
    ]

    return result


def get_video_statistics(youtube, video_id):
    result = {}
    res = youtube.videos().list(
        id=video_id,
        part="snippet,statistics,status,contentDetails",
    ).execute()

    commentaries = get_comment_list_statistics(youtube, video_id)

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
    result['comments'] = commentaries
    result['commentsCount'] = len(commentaries)
    return result


def get_comment_list_statistics(youtube, video_id):
    res = youtube.commentThreads().list(
        part="snippet,id",
        videoId=video_id,
        maxResults="50",
        order='relevance'
    ).execute()

    next_page_token = res.get('nextPageToken')
    while 'nextPageToken' in res:
        try:
            next_page = youtube.commentThreads().list(
                part="snippet,id",
                videoId=video_id,
                maxResults="50",
                pageToken=next_page_token,
                order='relevance'
            ).execute()
            res['items'] = res['items'] + next_page['items']
        except HttpError:
            pass

        if 'nextPageToken' not in next_page:
            res.pop('nextPageToken', None)
            break
        else:
            next_page_token = next_page['nextPageToken']
    result = [get_comment_inst(item) for item in res['items']]
    return result


def get_comment_inst(item):
    return {
        'commentText': item['snippet']['topLevelComment']['snippet']['textDisplay'],
        'authorChannelUrl': item['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
        'rate': item['snippet']['topLevelComment']['snippet']['likeCount'],
        'authorChannelId': item['snippet']['topLevelComment']['snippet']['authorChannelId']['value'],
    }


def get_comment_author_channel_url(item):
    return item['snippet']['topLevelComment']['snippet']['authorChannelUrl'] + '\n'
