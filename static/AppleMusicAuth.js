document.addEventListener('DOMContentLoaded', async () => {
    const developerToken = "{{ developer_token|safe }}"; // Injected from Flask

    MusicKit.configure({
        developerToken,
        app: {
            name: 'TuneBridge',
            build: '1.0.0'
        }
    });

    const music = MusicKit.getInstance();
    const appleBtn = document.querySelector('.btn-apple');

    async function sendTokensToBackend(userToken) {
        const response = await fetch('/apple-music-token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_token: userToken,
                developer_token: developerToken
            })
        });

        if (!response.ok) {
            const text = await response.text();
            console.error('Failed to send token:', text);
            alert('Error sending tokens to backend.');
        } else {
            const result = await response.json();
            console.log('Token stored on backend:', result);
        }
    }

    if (appleBtn) {
        appleBtn.addEventListener('click', async () => {
            try {
                let userToken = localStorage.getItem('apple_user_token');

                if (!userToken || !music.isAuthorized) {
                    userToken = await music.authorize();
                    localStorage.setItem('apple_user_token', userToken);
                    alert('Apple Music authentication successful!');
                } else {
                    alert('Already authorized with Apple Music!');
                }

                await sendTokensToBackend(userToken);
            } catch (err) {
                console.error('Authorization error:', err);
                alert('Apple Music login failed: ' + err.message);
            }
        });
    }

    // Optional helper functions for search and library
    window.searchAppleMusic = async (query) => {
        if (!music.isAuthorized) throw new Error('Not authorized with Apple Music');
        return await music.api.search(query, { types: ['songs', 'albums', 'playlists'], limit: 20 });
    };

    window.getAppleMusicLibrary = async () => {
        if (!music.isAuthorized) throw new Error('Not authorized with Apple Music');
        return await music.api.library.playlists();
    };
});