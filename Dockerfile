FROM python:3.13-slim

RUN apt-get update && apt-get install -y nodejs ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip install -U yt-dlp

COPY . .

CMD ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]