# TuneBridge 

TuneBridge is a web application that helps you manage and convert your Spotify playlists into apple music playlists

## Features

- Secure Spotify Authentication
- Search Playlists by Name

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- pip (Python package manager)

You'll also need:
- A Spotify Developer Account
- Spotify API Credentials (Client ID and Client Secret)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tune-bridge.git
cd tune-bridge
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Spotify API credentials:
```env
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
```

4. Run the application:
```bash
python main.py
```

The application will automatically open in your default web browser at `http://127.0.0.1:5000`.

## Getting Spotify API Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Set the redirect URI to `http://127.0.0.1:5000/callback`
4. Copy your Client ID and Client Secret to your `.env` file

## Current Features

- Spotify OAuth Authentication
- Search for a playlist in your library

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

