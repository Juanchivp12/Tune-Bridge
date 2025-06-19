document.addEventListener('DOMContentLoaded', async () => {

    // Replace with your developer token
    const developerToken = "Your token here";

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

                const userToken = await music.authorize();
                alert('Apple music authentication successful!');

                // Send token to backend for usage
                fetch('/apple-music-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_token: userToken })
                })
                    .then(res => res.json())
                    .then(data => {
                        alert('Apple Music token sent to backend');
                    })
                    .catch(err => {
                        alert('Error sending token to backend');
                    });

            } catch (e) {
                alert('Apple Music authentication failed');
            }

        });
    }

});