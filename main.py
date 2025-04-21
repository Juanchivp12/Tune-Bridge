import webbrowser

from flask import Flask, request, redirect, session, jsonify, render_template
import random
import requests
import urllib.parse
import dotenv
import os
import base64
from requests import get, post

dotenv.load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(32)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

BASE_URL = 'https://api.spotify.com/v1/'
AUTH_URL = 'https://accounts.spotify.com/authorize?'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Generate a random series of letters for the state
def generate_state():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.sample(letters, 16))

# Gets all the playlists of the authorized user
def get_all_playlists(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = get(BASE_URL + 'me/playlists', headers=headers)
    return response.json()['items']

def choose_playlist(playlists):
    pass
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    state = generate_state()
    scope = 'user-library-read playlist-read-private playlist-modify-private playlist-modify-public'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state,
        'scope': scope,
        'show_dialog': True
    }
    auth_url = AUTH_URL + urllib.parse.urlencode(params)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})

    if 'code' in request.args and 'state' in request.args:
        code = request.args.get('code')
        state = request.args.get('state')

        auth_body = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
        }
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8'),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = post(TOKEN_URL, headers=headers, data=auth_body)
        token_data = response.json()

        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        session['expires_in'] = token_data['expires_in']

        return redirect('/choose')

@app.route('/choose')
def choose_playlist():
    if 'access_token' not in session:
        return redirect('/login')
    if session['expires_in'] <= 0:
        return redirect('/refresh-token')

    playlists = get_all_playlists(session['access_token'])

    return render_template('choose.html', playlists=playlists)

@app.route('/refresh-token')
def refresh_token():
    pass

if __name__ == '__main__':
    webbrowser.open(REDIRECT_URI.strip('/callback'))
    app.run()

