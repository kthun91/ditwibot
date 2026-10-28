FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_DIR=/app/data \
    TZ=Europe/Berlin

RUN apt-get update \
 && apt-get install -y --no-install-recommends tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ditwibot.py ./
RUN useradd --uid 1000 --no-create-home bot && mkdir -p /app/data && chown bot /app/data
USER bot

CMD ["python", "ditwibot.py"]
