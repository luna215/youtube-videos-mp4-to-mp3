import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pydash as _

from moviepy.editor import *
from pytube import YouTube

from pprint import pprint

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "environment.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # Get list of personal playlists
    request = youtube.playlists().list(
        mine=True,
        part="id,snippet,contentDetails",
        maxResults=10,
    )
    response = request.execute()

    # Extract playlist that is titled 'to_download'
    playlists = response.get('items')
    to_download_playlist = _.head(_.filter_(playlists, {'snippet': {'title': 'to_download'}}))
    to_download_id = to_download_playlist.get('id')

    # Get playlist details
    request = youtube.playlistItems().list(
        part='id,contentDetails',
        playlistId=f'{to_download_id}'
    )
    response = request.execute()
    items = response.get('items')
    video_ids = _.map_(items, 'contentDetails.videoId')

    # Download YouTube video based on video Id
    for _id in video_ids:
        try:
            YouTube(f'https://www.youtube.com/watch?v={_id}').streams.first().download('./videos')
        except:
            print('Looks like there was an issue grabbing video %s', _id)

    # Convert MP4 file to MP3 file
    for file in os.listdir('videos'):
        if file == '.DS_Store':
            continue
        print('Currently processing file:', file)
        video = VideoFileClip(os.path.join('videos', file))
        file_name = file[:-3]
        extension = 'mp3'
        file_name += extension
        
        video.audio.write_audiofile(os.path.join('audio', file_name))

if __name__ == "__main__":
    main()