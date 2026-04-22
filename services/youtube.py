import os
import json
import yt_dlp
import requests
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal

class YoutubeService(QObject):
    download_started = pyqtSignal(str)
    download_finished = pyqtSignal(str, str)

    def __init__(self, download_dir="data/albums", json_path="data/albums.json"):
        super().__init__()
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.covers_dir = Path("data/covers")
        self.covers_dir.mkdir(parents=True, exist_ok=True)
        
        self.json_path = json_path
        self.all_albums = []
        self.load_local_data()

    def load_local_data(self):
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.all_albums = []
                    
                    if isinstance(data, dict):
                        for artist, albums in data.items():
                            for album in albums:
                                album['artist'] = artist 
                                self.all_albums.append(album)
                    else:
                        self.all_albums = data.get("albums", [])
                        
            print(f"[YoutubeService] Loaded {len(self.all_albums)} albums.")
        except Exception as e:
            print(f"YoutubeService (json): {e}")

    def search(self, query):
        query = query.lower().strip()
        if not query: return []
        return [a for a in self.all_albums if query in a['title'].lower() or query in a['artist'].lower()]

    def get_cover_path(self, album_id, url):
        if not url:
            return "assets/images/default_cover.png"

        local_path = self.covers_dir / f"{album_id}.jpg"
        
        if not local_path.exists():
            try:
                print(f"[YoutubeService] Downloading cover for {album_id}...")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                print(f"[YoutubeService] Cover download error: {e}")
                return "assets/images/default_cover.png"
                
        return str(local_path.absolute())

    def get_album_path(self, album_id):
        return self.download_dir / f"{album_id}.m4a"

    def prepare_and_get_path(self, album_id, url, title):
        path = self.get_album_path(album_id)
        
        if not path.exists():
            print(f"[YoutubeService] Downloading audio: {title}")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.download_dir / f"{album_id}.%(ext)s"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                }],
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        return str(path.absolute())

    def timestamp_to_ms(self, ts):
        parts = list(map(int, ts.split(':')))
        if len(parts) == 2: # MM:SS
            seconds = parts[0] * 60 + parts[1]
        elif len(parts) == 3: # HH:MM:SS
            seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        else:
            seconds = 0
        return seconds * 1000
    
    def get_track_time_range(self, album, track_index):
        tracks = album['tracks']
        start_ms = self.timestamp_to_ms(tracks[track_index]['start'])

        if track_index < len(tracks) - 1:
            end_ms = self.timestamp_to_ms(tracks[track_index + 1]['start'])
        else:
            end_ms = -1 
            
        return start_ms, end_ms