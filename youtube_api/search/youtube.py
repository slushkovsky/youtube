import requests
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'AIzaSyC7CmckF_e6weA0tWIJhWG0ozg0gFLFG9c'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

BASE_URL = "https://www.youtube.com/"
CHANNEL = 'channel/'
PLAYLIST = 'playlist/'

STARTS_WITH = (
    'https://www.youtube.com',
    'www.youtube.com',
    'youtube.com',
    'https://youtube.com'
)

DOMEN_NAMES = {
    'vk.com/': 'VK',
    'facebook.com/': 'Facebook',
    'twitter.com/': 'Twitter',
    'instagram.com/': 'Instagram',
    'youtube.com/': 'Youtube',
    'ok.ru/': 'Odnoklassniki',
}


def build_youtube():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    return youtube


def get_channel_id(link, youtube):
    if link.lower().startswith(tuple(STARTS_WITH)):
        list_of_elements = link.split('/')
        for index, item in enumerate(list_of_elements):
            if item == 'user':
                channels_list_response = youtube.channels().list(
                    forUsername=list_of_elements[index + 1],
                    part='id'
                ).execute()
                if channels_list_response['items']:
                    return channels_list_response['items'][0]['id']
            elif item == 'channel':
                return list_of_elements[index + 1]
        return 'Incorrect link'


def get_video_id(url):
    video_id = url.split('?')[-1]
    requests = video_id.split('&')
    for r in requests:
        parameter = r.split('=')
        if parameter[0] == 'v':
            return (parameter[-1])


def get_playlist_link(playlist_id):
    result = BASE_URL + PLAYLIST + '?list=' + playlist_id
    return result


def get_social_links(url):
    results = {}
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    links = soup.find_all('ul', {'class': 'about-custom-links'})
    if len(links) == 0:
        return {}

    links = links[-1]

    about_channel_link_list = links.find_all('li', {'class': 'channel-links-item'})
    for item in about_channel_link_list:
        # getting social link
        social_link = item.find('a').get('href')

        for key, value in DOMEN_NAMES.items():
            if key in social_link:
                results[value] = social_link
    return results


def get_social_links_comment_author(url):
    results = {}
    text = requests.get(url.replace('\n', '/about')).text
    soup = BeautifulSoup(text, 'html.parser')
    links = soup.find_all('ul', {'class': 'about-custom-links'})
    if links:
        about_channel_link_list = links[-1].find_all('li', {'class': 'channel-links-item'})
        if about_channel_link_list:
            for item in about_channel_link_list:
                # getting social link
                social_link = item.find('a').get('href')
                if social_link:
                    for key, value in DOMEN_NAMES.items():
                        if key in social_link:
                            results[social_link] = value
        if results:
            return results


def get_favorites(channels_list_response):
    # Validation data
    # Making full favorites link or Not allowed
    if not channels_list_response['items']:
        return 'Incorrect link'
    elif 'featuredChannelsUrls' in channels_list_response['items'][0]['brandingSettings']['channel'].keys():
        favorites_response = channels_list_response['items'][0]['brandingSettings']['channel']['featuredChannelsUrls']
    else:
        favorites_response = 'Not allowed'
    return favorites_response
