import googleapiclient.discovery
from html import unescape
from json import loads


def get_url(search_phrase: str):
    if not search_phrase.isprintable():
        return 'Invalid search phrase.'
    api_service_name = 'youtube'
    api_version = 'v3'
    key = <your API key>
    try:
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=key)
    except googleapiclient.discovery.HttpError as e:
        content = loads(e.content)
        return content['error']['message']
    request = youtube.search().list(
        part='snippet',
        maxResults=25,
        order='relevance',
        q=search_phrase,
        type='video'
    )
    result = request.execute()
    if result.get('items'):
        video = result.get('items')[0]
        id = video.get('id').get('videoId')
        title = unescape(video.get('snippet').get('title'))
        return f'[ {title} ] - https://youtu.be/{id}'
    return 'No results.'
