import os

import requests
from dotenv import load_dotenv

load_dotenv("./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"


def get_playlist_id():
    if not API_KEY:
        raise ValueError("API_KEY is missing. Check that .env contains API_KEY=...")

    url = "https://youtube.googleapis.com/youtube/v3/channels"
    params = {
        "part": "contentDetails",
        "forHandle": CHANNEL_HANDLE,
        "key": API_KEY,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    items = data.get("items", [])
    if not items:
        raise ValueError(f"No channel found for handle: {CHANNEL_HANDLE}")

    playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return playlist_id


if __name__ == "__main__":
    print(get_playlist_id())