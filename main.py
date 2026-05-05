import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

DOWNLOAD_DIR = Path("/tmp/downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

import os

cookies_content = os.getenv("YOUTUBE_COOKIES")
if cookies_content:
    with open("cookies.txt", "w") as f:
        f.write(cookies_content)

def cleanup_by_limit(max_files: int = 50):
    files = sorted(
        DOWNLOAD_DIR.glob("*"), 
        key=lambda x: x.stat().st_mtime
    )
    if len(files) > max_files:
        files_to_delete = files[:len(files) - max_files]
        
        for file in files_to_delete:
            try:
                file.unlink()
                print(f"Limite raggiunto. Eliminato il file più vecchio: {file.name}")
            except Exception as e:
                print(f"Errore eliminazione {file.name}: {e}")

app = FastAPI(title="Music Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def get_audio_file(video_id: str):
    for file in DOWNLOAD_DIR.glob(f"{video_id}.*"):
        if file.suffix == ".mp3":
            return file
    return None


def download_audio(video_id: str):
    
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "cookiefile" : "cookies.txt",
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
        }
    },
        'http_headers': {
        'User-Agent': 'Mozilla/5.0'},
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    cleanup_by_limit(max_files = 50)

    return get_audio_file(video_id)



@app.get("/search")
def search(q: str, limit: int = 20):
    with YoutubeDL({
        "quiet": True,
        "noplaylist": True,
        "extract_flat": True
    }) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{q}", download=False)

    return info



@app.get("/download/{video_id}")
def download(video_id: str):

    file_path = download_audio(video_id)

    if not file_path:
        raise HTTPException(status_code=404, detail="File non trovato")

    return FileResponse(file_path, media_type="audio/mpeg")


@app.get("/stream/{video_id}")
def stream(video_id: str):
    file_path = get_audio_file(video_id)

    if not file_path:
        file_path = download_audio(video_id)

    return FileResponse(file_path, media_type="audio/mpeg")






