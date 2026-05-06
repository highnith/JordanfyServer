FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl ffmpeg unzip && \
    curl -fsSL https://deno.land/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install -U "yt-dlp[default]"

COPY . .

CMD ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]