document.addEventListener('DOMContentLoaded', async () => {

    // You need to replace this with your actual developer token from Apple Developer Console
    const developerToken = "YOUR_DEVELOPER_TOKEN_HERE";

    // Configure MusicKit
    MusicKit.configure({
        developerToken: developerToken,
        app: {
            name: 'TuneBridge',
            build: '1.0.0'
        }
    });

    const music = MusicKit.getInstance();

    const appleBtn = document.querySelector('.btn-apple');
    if (appleBtn) {
        appleBtn.addEventListener('click', async () => {
            try {
                // Check if user is already authorized
                if (music.isAuthorized) {
                    alert('Already authorized with Apple Music!');
                    return;
                }

                // Request authorization
                const userToken = await music.authorize();
                console.log('Apple Music authorization successful');
                alert('Apple Music authentication successful!');

                // Send token to backend for usage
                const response = await fetch('/apple-music-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_token: userToken,
                        developer_token: developerToken
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    alert('Apple Music token sent to backend successfully');
                    console.log('Backend response:', data);
                } else {
                    throw new Error('Failed to send token to backend');
                }

            } catch (error) {
                console.error('Apple Music authentication error:', error);
                alert('Apple Music authentication failed: ' + error.message);
            }
        });
    }

    // Add function to search Apple Music
    window.searchAppleMusic = async (query) => {
        try {
            if (!music.isAuthorized) {
                throw new Error('Not authorized with Apple Music');
            }

            const results = await music.api.search(query, {
                types: ['songs', 'albums', 'playlists'],
                limit: 20
            });

            return results;
        } catch (error) {
            console.error('Apple Music search error:', error);
            throw error;
        }
    };

    // Add function to get user's Apple Music library
    window.getAppleMusicLibrary = async () => {
        try {
            if (!music.isAuthorized) {
                throw new Error('Not authorized with Apple Music');
            }

            const library = await music.api.library.playlists();
            return library;
        } catch (error) {
            console.error('Apple Music library error:', error);
            throw error;
        }
    };

});