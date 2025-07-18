import webbrowser
from flask import Flask, request, redirect, session, jsonify, render_template
import random
import urllib.parse
import dotenv
import os
import base64
from requests import get, post

dotenv.load_dotenv()

# Constants 
REDIRECT_URI = 'http://127.0.0.1:5000/callback'


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
def search_playlist(playlists, name, token):
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


class Spotify:
    def __init__(self, app):
        """
        Initializes the Spotify integration with the Flask app and loads credentials from environment variables.
        Args:
            app (Flask): The Flask application instance.
        """
        self.app = app
        self.CLIENT_ID = os.getenv('CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        self.BASE_URL = 'https://api.spotify.com/v1/'
        self.AUTH_URL = 'https://accounts.spotify.com/authorize?'
        self.TOKEN_URL = 'https://accounts.spotify.com/api/token'
        
        self.register_routes()


    def get_all_playlists(self, token):
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
        response = get(self.BASE_URL + 'me/playlists', headers=headers)
        return response.json()['items']

    def get_playlist(self, playlist_id, token):
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
        response = get(f'{self.BASE_URL}playlists/{playlist_id}', headers=headers)
        return response.json()
    
    def get_playlist_tracks(self, playlist_id, token):
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
        response = get(f'{self.BASE_URL}playlists/{playlist_id}/tracks', headers=headers)
        return response.json()['items']

    def register_routes(self):
        #Registers all Flask routes/endpoints for the Spotify integration.
        @self.app.route('/')
        def index():
            """Renders the landing page."""
            return render_template('index.html')

        @self.app.route('/login')
        def login():
            # Redirects the user to Spotify's OAuth login page.
            state = generate_state()
            scope = 'user-library-read playlist-read-private playlist-modify-private playlist-modify-public'
            params = {
                'client_id': self.CLIENT_ID,
                'response_type': 'code',
                'redirect_uri': REDIRECT_URI,
                'state': state,
                'scope': scope,
                'show_dialog': True
            }
            auth_url = self.AUTH_URL + urllib.parse.urlencode(params)
            return redirect(auth_url)

        @self.app.route('/callback')
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
                'Authorization': 'Basic ' + base64.b64encode(f'{self.CLIENT_ID}:{self.CLIENT_SECRET}'.encode('utf-8')).decode('utf-8'),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = post(self.TOKEN_URL, headers=headers, data=auth_body)
            token_data = response.json()

            session['access_token'] = token_data['access_token']
            session['refresh_token'] = token_data['refresh_token']
            session['expires_in'] = token_data['expires_in']

            return redirect('/choose')

        @self.app.route('/refresh-token')
        def refresh_token():
            """
            Placeholder for refreshing the Spotify access token.
            """
            pass

        @self.app.route('/choose')
        def choose():
            # Displays a list of the user's playlists to choose from.
            if 'access_token' not in session:
                return redirect('/login')
            if session['expires_in'] <= 0:
                return redirect('/refresh-token')

            playlists = self.get_all_playlists(session['access_token'])
            return render_template('choose.html', playlists=playlists)

        @self.app.route('/chosen-playlist', methods=['POST'])
        def chosen_playlist():
            """
            Handles the playlist selection, fetches tracks and artists, and displays them.
            """
            if 'access_token' not in session:
                return redirect('/login')

            token = session['access_token']
            playlists = self.get_all_playlists(token)
            playlist_name = request.form.get('playlist_name')
            
            if not playlist_name:
                return redirect('/choose')
            
            playlist_id = search_playlist(playlists, playlist_name, token)
            
            if not playlist_id:
                return "Playlist not found"
                
            playlist = self.get_playlist(playlist_id, token)
            
            if not playlist:
                return "Error fetching playlist details"
            
            # Store the playlist info 
            session['selected_playlist'] = {
                'name': playlist['name'],
                'tracks_url': playlist['tracks']['href'],
                'image_url': playlist['images'][0]['url'] if playlist['images'] else None
            }

            # Fetch tracks and artists
            tracks_data = self.get_playlist_tracks(playlist_id, token)
            tracks = []
            for item in tracks_data:
                track = item.get('track')
                if track:
                    track_name = track.get('name')
                    artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
                    tracks.append({'name': track_name, 'artists': artists})

            return render_template('playlist_tracks.html', playlist=playlist, tracks=tracks)

        @self.app.route('/convert')
        def convert():
            """
            Placeholder for playlist conversion logic.
            """
            pass


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(32)
    spotify = Spotify(app)
    return app

if __name__ == '__main__':
    app = create_app()
    webbrowser.open(REDIRECT_URI.strip('/callback'))
    app.run()

