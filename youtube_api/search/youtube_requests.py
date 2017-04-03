from googleapiclient.errors import HttpError


def get_all_playlists_links(youtube, channel_id):
    result = []
    res = youtube.playlists().list(
        part="id",
        channelId=channel_id,
        maxResults="50"
    ).execute()
    next_page_token = res.get('nextPageToken')
    while 'nextPageToken' in res:
        next_page = youtube.playlists().list(
            part="id",
            channelId=channel_id,
            maxResults="50",
            pageToken=next_page_token
        ).execute()
        res['items'] = res['items'] + next_page['items']
        if 'nextPageToken' not in next_page:
            res.pop('nextPageToken', None)
        else:
            next_page_token = next_page['nextPageToken']
    for item in res['items']:
        result.append(item['id'])

    sections = youtube.channelSections().list(
        part="snippet,contentDetails",
        channelId=channel_id,
    ).execute()

    for item in sections['items']:
        if item['snippet']['type'] == 'multiplePlaylists':
            result.extend(item['contentDetails']['playlists'])
    return result


def get_all_playlist_item_links(youtube, playlist_id):
    result = []
    res = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults="50"
    ).execute()

    next_page_token = res.get('nextPageToken')
    while 'nextPageToken' in res:
        next_page = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults="50",
            pageToken=next_page_token
        ).execute()
        res['items'] = res['items'] + next_page['items']

        if 'nextPageToken' not in next_page:
            res.pop('nextPageToken', None)
        else:
            next_page_token = next_page['nextPageToken']
    for item in res['items']:
        result.append(item['contentDetails']['videoId'])
    return result


def get_all_subs_links(youtube, channel_id):
    result = []
    try:
        res = youtube.subscriptions().list(
            channelId=channel_id,
            part="snippet",
        ).execute()
    except HttpError:
        return None

    next_page_token = res.get('nextPageToken')
    while 'nextPageToken' in res:
        next_page = youtube.subscriptions().list(
            part="snippet",
            channelId=channel_id,
            maxResults="50",
            pageToken=next_page_token
        ).execute()
        res['items'] = res['items'] + next_page['items']

        if 'nextPageToken' not in next_page:
            res.pop('nextPageToken', None)
        else:
            next_page_token = next_page['nextPageToken']
    for item in res['items']:
        result.append(
            {
                'channelId': item['snippet']['resourceId']['channelId'],
                'channelUrl': 'https://www.youtube.com/channel/' + item['snippet']['resourceId']['channelId']
            }
        )
    return result
