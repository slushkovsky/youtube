from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

from .statistics import get_playlist_statistics, get_comment_author_channel_url
from .youtube_requests import get_all_playlist_item_links, get_all_subs_links, get_all_playlists_links
from .youtube import get_channel_id, get_social_links, build_youtube, get_favorites, get_video_id, \
    get_social_links_comment_author


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


def get_channel_info(youtube, link):
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

    return response


def get_playlists_video_ids(youtube, playlist_id):
    rmaker = partial(
        youtube.playlistItems().list,
        part="snippet",
        playlistId=playlist_id,
        maxResults="50"
    )
    ids = [
        r['snippet']['resourceId']['videoId']
        for r in rmaker if r['snippet']['resourceId']['kind'] == 'youtube#video'
    ]
    return ids


def get_playlists_info(youtube, link):
    result = {}
    # Getting from the link channel_id and validate it
    channel_id = get_channel_id(link, youtube)
    playlists_id = get_all_playlists_links(youtube, channel_id)
    playlists_statistics = [
        get_playlist_statistics(youtube, i) for i in playlists_id
    ]
    result['playlistsInfo'] = playlists_statistics
    result['channelUrl'] = link
    result['channelId'] = channel_id
    result['playlistId'] = playlists_id
    result['playlistLink'] = link
    return result


def get_comment_author_url_list(url):
    video_id = get_video_id(url)
    pool = ThreadPool(10)
    youtube = build_youtube()
    res = youtube.commentThreads().list(
        part="snippet,id",
        videoId=video_id,
        maxResults="50",
        order='relevance'
    ).execute()

    next_page_token = res.get('nextPageToken')
    while 'nextPageToken' in res:
        next_page = youtube.commentThreads().list(
            part="snippet,id",
            videoId=video_id,
            maxResults="50",
            pageToken=next_page_token,
            order='relevance'
        ).execute()
        res['items'] = res['items'] + next_page['items']
        if 'nextPageToken' not in next_page:
            res.pop('nextPageToken', None)
        else:
            next_page_token = next_page['nextPageToken']
    result = pool.map(get_comment_author_channel_url, res['items'])
    pool.close()
    pool.join()

    with open('comment-author-links.txt', 'w') as outfile:
        for item in result:
            outfile.write(item)
    return result


def get_socials_comment_author(url):
    video_link_list = get_comment_author_url_list(url)
    pool = ThreadPool(10)
    result = pool.map(get_social_links_comment_author, video_link_list)
    pool.close()
    pool.join()
    with open('comment-author-socials.txt', 'w') as outfile:
        for item in result:
            if item:
                for key in item.keys():
                    outfile.write(key + '\n')

    return result
