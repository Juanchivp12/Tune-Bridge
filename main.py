import dotenv
import os
import base64
import json
import requests
from requests import get, post
dotenv.load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# Gets the token
def get_token():
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    token = response.json()
    return token

# Variable holding the access token
access_token = get_token()['access_token']
#
# def get_artists_albums(token):
#     url = f'https://api.spotify.com/v1/artists/{'1uNFoZAHBGtllmzznpCI3s'}/albums'
#
#     headers = {
#         'Authorization': f'Bearer {token}'
#     }
#
#     params = {
#         'include_groups': 'album',
#         'limit': 10
#     }
#
#     response = requests.get(url, headers=headers, params=params)
#     return response.json()
#
#
# albums = get_artists_albums(access_token)
#
# for i, album in enumerate(albums['items'], start=1):
#     print(f'{i}. {album["name"]}, Released {album["release_date"]}')

def get_playlist_id():
    playlist_url = input('Paste the Spotify playlist URL or URI: ')

    if 'playlist/' in playlist_url:
        return playlist_url.split('playlist/')[1].split('?')[0]
    elif 'spotify:playlist:' in playlist_url:
        return playlist_url.split('spotify:playlist:')[1]
    else:
        raise ValueError("❌ Invalid playlist URL or URI.")

playlist_id = get_playlist_id()

def get_playlist_items(token):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'market' : 'US'
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

tracks = get_playlist_items(access_token)
print(json.dumps(tracks, indent=2))

for i, track in enumerate(tracks['items'], start=1):
    print(f'{i}. {track["track"]["name"]}')





