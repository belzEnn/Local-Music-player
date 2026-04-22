import os
import json
import yt_dlp
import requests
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class YoutubeService(QObject):
    # Сигналы для будущего (чтобы UI знал, когда закончили)
    download_started = pyqtSignal(str)
    download_finished = pyqtSignal(str, bool)

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
        """Просто грузит JSON в память. Это быстро и не качает файлы."""
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
                        # Если структура — список
                        self.all_albums = data.get("albums", [])
                        
            print(f"[YoutubeService] Loaded {len(self.all_albums)} albums from JSON.")
        except Exception as e:
            print(f"YoutubeService (load_local_data) error: {e}")

    def search(self, query):
        """Поиск по уже загруженным метаданным."""
        query = query.lower().strip()
        if not query: return []
        return [a for a in self.all_albums if query in a['title'].lower() or query in a['artist'].lower()]

    def get_album_details(self, album_id):
        """Возвращает полные данные об альбоме по его ID."""
        for album in self.all_albums:
            if album['id'] == album_id:
                return album
        return None

    def is_album_downloaded(self, album_id):
        """Проверяет, существует ли уже файл альбома на диске."""
        return self.get_album_path(album_id).exists()

    def get_cover_path(self, album_id, url):
        """Минимальная скачка — только обложка (если нет)."""
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
        """Просто возвращает объект Path к файлу."""
        return self.download_dir / f"{album_id}.m4a"

    def download_album(self, album_id, url):
        """Явное скачивание альбома через yt_dlp."""
        path = self.get_album_path(album_id)
        
        if path.exists():
            return True # Уже есть

        try:
            print(f"[YoutubeService] Manual download started: {url}")
            self.download_started.emit(album_id)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.download_dir / f"{album_id}.%(ext)s"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            success = path.exists()
            self.download_finished.emit(album_id, success)
            return success

        except Exception as e:
            print(f"[YoutubeService] Download failed: {e}")
            self.download_finished.emit(album_id, False)
            return False

    def prepare_and_get_path(self, album_id, url, title):
        """
        Теперь эта функция ПРОСТО возвращает путь. 
        Она больше не качает сама (для безопасности).
        """
        path = self.get_album_path(album_id)
        if not path.exists():
            return "" # Возвращаем пустоту, если файла нет
        return str(path.absolute())

    def timestamp_to_ms(self, ts):
        """Перевод MM:SS или HH:MM:SS в миллисекунды."""
        try:
            parts = list(map(int, ts.split(':')))
            if len(parts) == 2: # MM:SS
                seconds = parts[0] * 60 + parts[1]
            elif len(parts) == 3: # HH:MM:SS
                seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
            else:
                seconds = 0
            return seconds * 1000
        except:
            return 0
    
    def get_track_time_range(self, album, track_index):
        """Определяет начало и конец трека внутри одного файла."""
        tracks = album.get('tracks', [])
        if not tracks or track_index >= len(tracks):
            return 0, -1

        start_ms = self.timestamp_to_ms(tracks[track_index]['start'])

        if track_index < len(tracks) - 1:
            end_ms = self.timestamp_to_ms(tracks[track_index + 1]['start'])
        else:
            end_ms = -1 # До конца файла
            
        return start_ms, end_ms
    
    def delete_album(self, album_id):
        """Безопасное удаление файлов альбома"""
        try:
            path = self.get_album_path(album_id)
            if path.exists():
                os.remove(path)
            
            return True
        except Exception as e:
            print(f"Error deleting album files: {e}")
            return False
        
class DownloadWorker(QThread):
    finished = pyqtSignal(bool)
    
    def __init__(self, service, album_id, url):
        super().__init__()
        self.service = service
        self.album_id = album_id
        self.url = url

    def run(self):
        success = self.service.download_album(self.album_id, self.url)
        self.finished.emit(success)