from flask import Flask, request, redirect
import random
import requests
import urllib.parse
import dotenv
import os
import base64
from requests import get, post
app = Flask(__name__)
dotenv.load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
BASE_URL = 'https://api.spotify.com'

# Generate a random series of letters for the state
def generate_state():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.sample(letters, 16))
@app.route('/')
def index():
    return redirect('/login')

@app.route('/login')
def login():
    url = 'https://accounts.spotify.com/authorize?'
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
    auth_url = url + urllib.parse.urlencode(params)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    url = 'https://accounts.spotify.com/api/token'

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8'),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = post(url, headers=headers, data=data)
    response.raise_for_status()
    token = response.json()['access_token']
    return token

if __name__ == '__main__':
    app.run()

