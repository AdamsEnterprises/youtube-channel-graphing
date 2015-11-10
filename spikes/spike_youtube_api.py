from __future__ import print_function, absolute_import
from apiclient import discovery

API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

CHANNEL_ID_PEWDIEPIE = 'UC-lHJZR3Gqxm24_Vd_AJ5Yw'


def youtube_build_api():
    youtube = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                              developerKey=API_KEY)
    return youtube


def main_runner():
    api = youtube_build_api()
    channel_sections = api.channelSections()
    response = channel_sections.list(part='snippet',
                                     channelId=CHANNEL_ID_PEWDIEPIE).execute()
    multiple_channels_ids = []
    for item in  response['items']:
        print (item)
        if item['snippet']['type'] == 'multipleChannels':
            multiple_channels_ids.append(item['id'])
    print (multiple_channels_ids)

if __name__ == '__main__':
    main_runner()

