from __future__ import print_function, absolute_import
from apiclient import discovery

API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

BASE_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'


def youtube_build_api():
    youtube = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                              developerKey=API_KEY)
    return youtube


def main_runner():
    api = youtube_build_api()
    response = api.channels().list(part='brandingSettings', id=BASE_CHANNEL_ID).execute()
    base_channel = response['items'][0]['brandingSettings']['channel']
    print (base_channel['title'], BASE_CHANNEL_ID)

    for id in base_channel['featuredChannelsUrls']:
        response = api.channels().list(part='brandingSettings', id=id).execute()
        channel = response['items'][0]['brandingSettings']['channel']
        print (channel['title'], id)

if __name__ == '__main__':
    main_runner()

