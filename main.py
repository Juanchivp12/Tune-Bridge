import webbrowser
from flask import Flask, request, redirect, session, jsonify, render_template
import random
import urllib.parse
import dotenv
import os
import base64
from requests import get, post
import jwt
import time

dotenv.load_dotenv()

# Constants 
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

# Spotify Constants
SPOTIFY_CLIENT_ID = os.getenv('CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SPOTIFY_BASE_URL = 'https://api.spotify.com/v1/'
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize?'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'


# Generates a random state for the OAuth flow
def generate_state():
    """
    Generates a random 16-character string for use as the OAuth state parameter.
    Returns:
        str: A random string of lowercase letters.
    """
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.sample(letters, 16))

# Searches for a playlist by name
def search_spotify_playlist(playlists, name, token):
    """
    Searches for a playlist by name in the user's playlists.
    Args:
        playlists (list): List of playlist objects.
        name (str): Name (or partial name) of the playlist to search for.
        token (str): Spotify access token (not used in this function).
    Returns:
        str or None: The playlist ID if found, else None.
    """
    for playlist in playlists:
        if name.lower() in playlist['name'].lower():
            return playlist['id']
    return None

# Creates a new playlist on apple music
def create_apple_music_playlist(playlist_name, dev_token, user_token):
    url = 'https://api.music.apple.com/v1/me/library/playlists'

    headers = {
        'Authorization': f'Bearer {dev_token}',
        'Music-User-Token': user_token,
        'Content-Type': 'application/json'
    }

    data = {
        "attributes": {
            'name': playlist_name,
            'description': 'playlist from spotify'
        }
    }

    response = post(url, headers=headers, json=data)

    if response.status_code == 201:
        playlist = response.json().get('data')[0]
        return {'success': True, 'playlist_id': playlist['id']}
    else:
        return {
            'error': 'Failed to create playlist',
            'status': response.status_code,
            'details': response.text
        }

# Searches for a song in the Apple Music US catalog
def search_apple_music_track(artist_name, track_name, dev_token, user_token):
    url = "https://api.music.apple.com/v1/catalog/us/search"

    params = {
        'term': f"{artist_name} {track_name}",
        'types': 'songs',
        'limit': 1
    }

    headers = {
        'Authorization': f'Bearer {dev_token}',
        'Music-User-Token': user_token
    }

    # Send a response to then get the song ID
    response = get(url, headers=headers, params=params)
    data = response.json()

    try:
        track_id = data['results']['songs']['data'][0]['id']
        return track_id
    except (KeyError, IndexError):
        return None

def add_song_apple_music_library(track_id, dev_token, user_token):
    url = 'https://api.music.apple.com/v1/me/library'

    headers = {
        'Authorization': f'Bearer {dev_token}',
        'Music-User-Token': user_token,
        'Content-Type': 'application/json'
    }

    params = {
        'ids[songs]': track_id,
    }

    response = post(url, headers=headers, params=params)

    return response.status_code == 202 or response.status_code == 204

def get_apple_music_library_song_id(artist_name, track_name, dev_token, user_token):
    url = 'https://api.music.apple.com/v1/me/library/search'
    headers = {
        'Authorization': f'Bearer {dev_token}',
        'Music-User-Token': user_token,
    }

    params = {
        'term': f"{artist_name} {track_name}",
        'types': 'library-songs',
        'limit': 1
    }

    # Retry up to 5 times in case it hasn't synced yet
    for i in range(5):
        response = get(url, headers=headers, params=params)
        data = response.json()

        print(f"[Attempt {i+1}] Searching for library track: {artist_name} - {track_name}")
        print("Library search response:", data)

        try:
            return data['results']['library-songs']['data'][0]['id']
        except (KeyError, IndexError):
            time.sleep(3)  # wait a bit and retry

    return None


def add_song_apple_music_playlist(library_track_id, playlist_id, dev_token, user_token):
    url = f'https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks'

    if not library_track_id:
        return {'error': 'track_id is None — cannot add to playlist'}

    headers = {
        'Authorization': f'Bearer {dev_token}',
        'Music-User-Token': user_token,
        'Content-Type': 'application/json'
    }

    body = {
        'data': [
            {
            'id': str(library_track_id),
            'type': 'songs',
            }
        ]
    }

    response = post(url, headers=headers, json=body)
    print("Track added:", library_track_id, "Status:", response.status_code)
    print("Response body:", response.text)

    if response.status_code == 204:
        return {'success': True, 'message': 'Song added to playlist'}
    else:
        return {
            'error': 'Failed to add song',
            'status': response.status_code,
            'details': response.text
        }

# Generates an apple developer token
def generate_apple_dev_token():
    team_id = os.getenv('TEAM_ID')
    key_id = os.getenv('KEY_ID')
    private_key = os.getenv('PRIVATE_KEY')

    headers = {
        'alg': 'ES256',
        'kid': key_id
    }

    payload = {
        'iss': team_id,
        'iat': int(time.time()),
        'exp': int(time.time()) + 86400,
    }

    return jwt.encode(payload, private_key, algorithm='ES256', headers=headers)

def get_all_playlists(token):
    """
    Fetches all playlists from the user's Spotify library.
    Args:
        token (str): Spotify access token.
    Returns:
        list: List of playlist objects.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = get(SPOTIFY_BASE_URL + 'me/playlists', headers=headers)
    return response.json()['items']

def get_playlist(playlist_id, token):
    """
    Fetches a specific playlist by its ID.
    Args:
        playlist_id (str): The Spotify playlist ID.
        token (str): Spotify access token.
    Returns:
        dict or None: Playlist object if found, else None.
    """
    if not playlist_id:
        return None

    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = get(f'{SPOTIFY_BASE_URL}playlists/{playlist_id}', headers=headers)
    return response.json()
    
def get_playlist_tracks(playlist_id, token):
    """
    Fetches all tracks from a specific playlist by its ID.
    Args:
        playlist_id (str): The Spotify playlist ID.
        token (str): Spotify access token.
    Returns:
        list: List of track objects in the playlist.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = get(f'{SPOTIFY_BASE_URL}playlists/{playlist_id}/tracks', headers=headers)
    return response.json()['items']

def register_routes(app):
    #Registers all Flask routes/endpoints for the Spotify integration.
    @app.route('/')
    def index():
        """Renders the landing page."""
        return render_template('index.html')

    @app.route('/login')
    def login():
        # Redirects the user to Spotify's OAuth login page.
        state = generate_state()
        scope = 'user-library-read playlist-read-private playlist-modify-private playlist-modify-public'
        params = {
            'client_id': SPOTIFY_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'state': state,
            'scope': scope,
            'show_dialog': True
        }
        auth_url = SPOTIFY_AUTH_URL + urllib.parse.urlencode(params)
        return redirect(auth_url)

    @app.route('/callback')
    def callback():
        """
        Handles the redirect from Spotify after user login, exchanges code for access token.
        """
        if 'error' in request.args:
            return jsonify({'error': request.args['error']})
        if 'code' not in request.args or 'state' not in request.args:
            # Add proper error handling
            return 'Code or state not found'

        code = request.args.get('code')
        state = request.args.get('state')

        auth_body = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
        }
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'.encode('utf-8')).decode('utf-8'),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = post(SPOTIFY_TOKEN_URL, headers=headers, data=auth_body)
        token_data = response.json()

        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        session['expires_in'] = token_data['expires_in']

        return redirect('/choose')

    @app.route('/refresh-token')
    def refresh_token():
        """
        Placeholder for refreshing the Spotify access token.
        """
        pass

    @app.route('/choose')
    def choose():
        # Displays a list of the user's playlists to choose from.
        if 'access_token' not in session:
            return redirect('/login')
        if session['expires_in'] <= 0:
            return redirect('/refresh-token')

        playlists = get_all_playlists(session['access_token'])
        developer_token = generate_apple_dev_token()
        return render_template('choose.html', playlists=playlists, developer_token=developer_token)

    @app.route('/chosen-playlist', methods=['POST'])
    def chosen_playlist():
        """
        Handles the playlist selection, fetches tracks and artists, and displays them.
        """
        if 'access_token' not in session:
            return redirect('/login')

        if session.get('expires_in') <= 0:
            return redirect('/refresh-token')

        token = session['access_token']
        playlists = get_all_playlists(token)
        playlist_name = request.form.get('playlist_name')

        if not playlist_name:
            return redirect('/choose')

        playlist_id = search_spotify_playlist(playlists, playlist_name, token)

        if not playlist_id:
            return "Playlist not found"

        playlist = get_playlist(playlist_id, token)

        if not playlist:
            return "Error fetching playlist details"

        try:
            session['apple_developer_token'] = generate_apple_dev_token()
        except Exception as e:
            return f"Error generating apple developer token: {str(e)}", 500

        # Store the playlist info
        session['selected_playlist'] = {
            'name': playlist['name'],
            'tracks_url': playlist['tracks']['href'],
            'image_url': playlist['images'][0]['url'] if playlist['images'] else None
        }

        # Fetch tracks and artists
        tracks_data = get_playlist_tracks(playlist_id, token)
        tracks = []
        for item in tracks_data:
            track = item.get('track')
            if track:
                track_name = track.get('name')
                artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
                album = track.get('album', {}).get('name', '')
                tracks.append({
                    'name': track_name,
                    'artists': artists,
                    'album': album
                })

        session['tracks'] = tracks

        return render_template('playlist_tracks.html', playlist=playlist, tracks=tracks, developer_token=session['apple_developer_token'])

    @app.route('/apple-music-token', methods=['POST'])
    def receive_apple_music_token():
        data = request.get_json()
        user_token = data.get('user_token')
        developer_token = data.get('developer_token')

        if not user_token or not developer_token:
            return jsonify({'error': 'Missing Apple Music Tokens'}), 400

        session['apple_music_token'] = user_token
        session['apple_developer_token'] = developer_token

        return jsonify({'message': 'Tokens received successfully'}), 200

    @app.route('/convert')
    def convert():
        if 'access_token' not in session:
            return redirect('/login')

        dev_token = session.get('apple_developer_token')
        user_token = session.get('apple_music_token')

        if not user_token or not dev_token:
            return jsonify(
                {'error': 'Apple Music tokens are missing. Please authenticate with Apple Music again.'}), 400

        playlist_name = session['selected_playlist']['name']
        playlist_response = create_apple_music_playlist(playlist_name, dev_token, user_token)
        playlist_id = playlist_response['playlist_id']
        if not playlist_id:
            return jsonify({'error': 'Failed to create Apple Music playlist'}), 500

        tracks = session['tracks']

        not_found_tracks = []

        for track in tracks:
            artist_name = track['artists']
            track_name = track['name']

            track_id = search_apple_music_track(artist_name, track_name, dev_token, user_token)
            if not track_id:
                not_found_tracks.append(track)
            else:
                added_to_library = add_song_apple_music_library(track_id, dev_token, user_token)
                if added_to_library:
                    time.sleep(3)
                    # library_song_id = get_apple_music_library_song_id(artist_name, track_name, dev_token, user_token)
                    result = add_song_apple_music_playlist(track_id, playlist_id, dev_token, user_token)
                    print("Add result:", result)
                else:
                    print("Failed to add track:", track)

        return jsonify({'success': True, 'message': 'Playlist successfully converted and tracks added.', 'tracks not found': not_found_tracks}), 200


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(32)
    return app

if __name__ == '__main__':
    app = create_app()
    register_routes(app)
    webbrowser.open(REDIRECT_URI.strip('/callback'))
    app.run()

