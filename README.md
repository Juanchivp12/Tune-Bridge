#  Tune Bridge (WIP)

**Tune Bridge** is a work-in-progress tool that lets you convert a Spotify playlist into an Apple Music playlist — and vice versa.

---

##  Features

- OAuth2 Authorization Code Flow with Spotify
- Fetch songs from any user playlist (public or private)
- Export to Apple Music (coming soon)

---

##  Tech Stack

- **Python 3**
- **Flask** – Web framework to handle routing and server logic
- **HTML & CSS** – Frontend for user interface
- **urllib** – To handle URL encoding and requests (used in the auth flow)
- **requests** – For making HTTP requests to the Spotify API
- **dotenv** – For managing sensitive environment variables
- **Spotify Web API** – Native usage (no Spotipy)


---

##  How to Use (Local Dev Only)

>  **You need your own Spotify Developer App credentials for now.**  
> This will be simplified when the app is deployed for public use.

```bash
# 1. Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# 2. (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Then open .env and replace with your own Spotify client_id, client_secret, and redirect_uri
# You can get these from https://developer.spotify.com/dashboard

# 5. Run the app
python app.py
