# TuneBridge 

TuneBridge is a web application that converts your Spotify playlists to Apple Music playlists seamlessly. Simply authenticate with both services, select a Spotify playlist, and let TuneBridge do the rest!

## Features

- **Spotify Integration**: Secure OAuth authentication and playlist browsing
- **Apple Music Integration**: Create playlists and add songs to your Apple Music library
- **Playlist Conversion**: Convert entire Spotify playlists to Apple Music with track matching
- **Track Search & Matching**: Intelligent search to find corresponding tracks in Apple Music
- **User-Friendly Interface**: Clean web interface for easy playlist selection and conversion
- **Detailed Results**: Shows which tracks were successfully converted and which weren't found

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- pip (Python package manager)

You'll also need:
- A Spotify Developer Account with API credentials
- An Apple Developer Account with MusicKit credentials
- Active subscriptions to both Spotify and Apple Music

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

3. Create a `.env` file in the root directory with your API credentials:
```env
# Spotify API Credentials
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret

# Apple Music API Credentials
TEAM_ID=your_apple_team_id
KEY_ID=your_apple_key_id
PRIVATE_KEY=your_apple_private_key
```

4. Run the application:
```bash
python main.py
```

The application will automatically open in your default web browser at `http://127.0.0.1:5000`.

## Live Demo

🚀 **Try the live version**: [https://tune-bridge.onrender.com](https://tune-bridge.onrender.com)

*Note: The app may take 30 seconds to wake up if it hasn't been used recently (free tier limitation).*

## Getting API Credentials

### Spotify API Setup
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Set the redirect URIs to:
   - `http://127.0.0.1:5000/callback` (for local development)
   - `https://tune-bridge.onrender.com/callback` (for live deployment)
4. Copy your Client ID and Client Secret to your `.env` file

### Apple Music API Setup
1. Join the [Apple Developer Program](https://developer.apple.com/programs/)
2. Create a MusicKit identifier in your Apple Developer account
3. Generate a private key for MusicKit
4. Add your Team ID, Key ID, and Private Key to your `.env` file

## How It Works

1. **Authenticate**: Log in with your Spotify account
2. **Select Playlist**: Choose any of your Spotify playlists
3. **Authenticate Apple Music**: Grant permission to access your Apple Music library
4. **Convert**: The app will:
   - Create a new playlist in Apple Music with the same name
   - Search for each track in the Apple Music catalog
   - Add found tracks to your Apple Music library
   - Add tracks to the new playlist
5. **Review Results**: See which tracks were successfully converted and which weren't found

## Technical Details

- **Backend**: Flask web framework with Python
- **Authentication**: OAuth 2.0 for Spotify, JWT tokens for Apple Music
- **APIs**: Spotify Web API and Apple Music API
- **Frontend**: HTML templates with JavaScript for Apple Music integration

## Limitations

- Some tracks may not be available in both catalogs
- Requires active subscriptions to both services
- Apple Music API has regional restrictions
- Track matching is based on artist and song name, may not be 100% accurate

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes. Please respect the terms of service for both Spotify and Apple Music APIs.

