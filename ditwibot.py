#!/usr/bin/env python3
"""Meldet in Discord, wenn ein Twitch-Kanal live geht.
Konfiguration über Umgebungsvariablen (siehe .env.example)."""
import json
import os
import time
import traceback
from datetime import datetime

import requests


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} ist nicht gesetzt (siehe .env.example).")
    return value


TWITCH_CHANNEL = env("TWITCH_CHANNEL")
TWITCH_CHANNEL_ID = env("TWITCH_CHANNEL_ID")
TWITCH_CLIENT_ID = env("TWITCH_CLIENT_ID")
TWITCH_SECRET = env("TWITCH_SECRET")
DISCORD_WEBHOOK_ID = env("DISCORD_WEBHOOK_ID")
DISCORD_WEBHOOK_TOKEN = env("DISCORD_WEBHOOK_TOKEN")

DATA_DIR = os.environ.get("DATA_DIR", ".")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
TIME_INTERVAL = 60  # Sekunden zwischen zwei Abfragen
TIMEOUT = 15  # Sekunden – verhindert endloses Hängen

access_token = None


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def redact(text):
    """Geheimnisse aus Fehlermeldungen entfernen."""
    text = str(text)
    for secret in (TWITCH_SECRET, DISCORD_WEBHOOK_TOKEN, access_token):
        if secret:
            text = text.replace(secret, "***")
    return text


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


def refresh_access_token():
    global access_token
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_SECRET,
            "grant_type": "client_credentials",
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    access_token = r.json()["access_token"]
    log("Neues Twitch-Token geholt.")


def get_stream():
    """Stream-Daten, wenn der Kanal live ist, sonst None. Wirft bei Fehlern."""
    if access_token is None:
        refresh_access_token()
    for attempt in range(2):
        r = requests.get(
            "https://api.twitch.tv/helix/streams",
            params={"user_id": TWITCH_CHANNEL_ID},
            headers={"Client-Id": TWITCH_CLIENT_ID, "Authorization": f"Bearer {access_token}"},
            timeout=TIMEOUT,
        )
        if r.status_code == 401 and attempt == 0:
            refresh_access_token()  # Token abgelaufen -> neu holen, einmal wiederholen
            continue
        r.raise_for_status()
        data = r.json().get("data", [])
        return data[0] if data else None


def send_discord(text):
    r = requests.post(
        f"https://discord.com/api/v10/webhooks/{DISCORD_WEBHOOK_ID}/{DISCORD_WEBHOOK_TOKEN}",
        json={"content": text},
        timeout=TIMEOUT,
    )
    r.raise_for_status()


def check(state):
    stream = get_stream()
    if stream is None:
        if state.get("live"):
            log("Stream offline.")
            state["live"] = False
            save_state(state)
        return

    # Jeder Stream hat eine eigene ID -> nur einmal pro Stream melden,
    # auch nach Fehlern oder einem Neustart des Containers.
    if stream["id"] == state.get("announced_stream_id"):
        return

    title = stream.get("title", "")
    game = stream.get("game_name", "")
    log(f"Live: {title} ({game})")
    send_discord(
        "I am live! Come watch me at : https://twitch.tv/" + TWITCH_CHANNEL
        + "\nTitle : " + title
        + "\nPlaying : " + game
    )
    state.update(live=True, announced_stream_id=stream["id"])
    save_state(state)
    log("In Discord gemeldet.")


def main():
    log(f"twBot gestartet: Kanal {TWITCH_CHANNEL}, Intervall {TIME_INTERVAL} s")
    state = load_state()
    while True:
        try:
            check(state)
        except Exception:
            log("Fehler – nächster Versuch im normalen Intervall:")
            print(redact(traceback.format_exc()), flush=True)
        time.sleep(TIME_INTERVAL)


if __name__ == "__main__":
    main()
