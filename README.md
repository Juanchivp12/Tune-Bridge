# 🎵 Tune Bridge (WIP)

**Tune Bridge** is a work-in-progress tool that lets you convert a spotify playlist into an apple music playlist and viceversa

---

## 🚀 Features

- OAuth2 Authorization Code Flow with Spotify
- Fetch songs from any user playlist (public or private)
- Export to Apple Music (coming soon)

---

## 🛠️ Tech Stack

- Python 3
- `requests` for API calls
- `dotenv` for secure environment variables
- Native Spotify Web API (no Spotipy)

---

## 🧪 How to Use

# 1. Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# 2. (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Then edit the .env file with your own credentials

# 5. Run the app
python app.py  # Or flask run / uvicorn main:app / whatever fits your project
