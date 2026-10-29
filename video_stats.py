import json
import os
import sys
import requests
from dotenv import load_dotenv
from datetime import date
load_dotenv("./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
max_results = 50  # Maximum number of results to fetch per request

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


def get_video_ids(playlist_id):
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={{playlist_id}}&key={{API_KEY}}"
    video_ids = []
    page_token = None
    try:
        while True:
            url = base_url.format(playlist_id=playlist_id, API_KEY=API_KEY)
            if page_token:
                url += f"&pageToken={page_token}"

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            for item in data.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            page_token = data.get("PageToken")
            if not page_token:
                break

        return video_ids
    except requests.exceptions.RequestException as e:
        print(f"Error fetching video IDs: {e}")
        sys.exit(1)




def extract_video_data(video_ids):
    extracted_data = []
    
    def batch_list(video_ids, batch_size=50):
        for i in range(0, len(video_ids), batch_size):
            yield video_ids[i:i + batch_size]
            
    "https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id=Y8IJi7iP5vk&key=[YOUR_API_KEY]"
    
    try:
        for batch in batch_list(video_ids):
            ids = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={ids}&key={API_KEY}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            extracted_data.extend(data.get("items", []))
            for item in data.get("items", []):
                video_id = item["id"]
                title = item["snippet"]["title"]
                description = item["snippet"]["description"]
                published_at = item["snippet"]["publishedAt"]
                view_count = item["statistics"].get("viewCount", 0)
                like_count = item["statistics"].get("likeCount", 0)
                comment_count = item["statistics"].get("commentCount", 0)
                video_data = {
                    "video_id": video_id,
                    "snippet": item["snippet"],
                    "statistics": item["statistics"],
                    "view_count": view_count,
                    "like_count": like_count,
                    "comment_count": comment_count, 
                }
            extracted_data.append(video_data)
        return extracted_data
    
    except requests.exceptions.RequestException as e:
        raise e
    

def save_to_json(extracted_data):
   file_path = f"./data/YT_data{date.today()}.json"
   
   with open(file_path, "w", encoding="utf-8") as json_output_file:
       json.dump(extracted_data, json_output_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    playlist_id = get_playlist_id()
    print(get_video_ids(playlist_id))
    video_ids = get_video_ids(playlist_id)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)
