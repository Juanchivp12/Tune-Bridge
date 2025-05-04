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
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.sample(letters, 16))

 # Searches for a playlist by name
def search_playlist(playlists, name, token):
    for playlist in playlists:
        if name.lower() in playlist['name'].lower():
            return playlist['id']
    return None


class Spotify:
    def __init__(self, app):
        self.app = app
        self.CLIENT_ID = os.getenv('CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        self.BASE_URL = 'https://api.spotify.com/v1/'
        self.AUTH_URL = 'https://accounts.spotify.com/authorize?'
        self.TOKEN_URL = 'https://accounts.spotify.com/api/token'
        
        self.register_routes()


    # Gets all playlists from the user's library
    def get_all_playlists(self, token):
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = get(self.BASE_URL + 'me/playlists', headers=headers)
        return response.json()['items']

    # Gets a playlist by id
    def get_playlist(self, playlist_id, token):
        if not playlist_id:
            return None
            
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = get(f'{self.BASE_URL}playlists/{playlist_id}', headers=headers)
        return response.json()
    
    # Registers routes
    def register_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/login')
        def login():
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
            if 'error' in request.args:
                return jsonify({'error': request.args['error']})
            if 'code' or 'state' not in request.args:
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
            pass

        @self.app.route('/choose')
        def choose():
            if 'access_token' not in session:
                return redirect('/login')
            if session['expires_in'] <= 0:
                return redirect('/refresh-token')

            playlists = self.get_all_playlists(session['access_token'])
            return render_template('choose.html', playlists=playlists)

        @self.app.route('/chosen-playlist', methods=['POST'])
        def chosen_playlist():
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

            return redirect('/convert')

        @self.app.route('/convert')
        def convert():
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

