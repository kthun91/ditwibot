#!/usr/bin/env python3
# python ditwibot.py TWITCH_CHANNEL TWITCH_CHANNEL_ID TWITCH_CLIENT_ID TWITCH_SECRET DISCORD_WEBHOOK_ID DISCORD_WEBHOOK_TOKEN
import sys
import time
import json
import requests
from discord import Webhook, RequestsWebhookAdapter

# Discord
DISCORD_WEBHOOK_ID = sys.argv[5]
DISCORD_WEBHOOK_TOKEN = sys.argv[6]

# twitch api from oauthToken.py
TWITCH_CLIENT_ID = sys.argv[3]
TWITCH_OAUTH_TOKEN = '' # will expire after 60 days -- will be generated anyway
TWITCH_SECRET = sys.argv[4] # do not share!

# twitch channel and user_id from userID.py
TWITCH_CHANNEL = sys.argv[1]
TWITCH_CHANNEL_ID = sys.argv[2]

TWITCH_USER_URL = 'https://api.twitch.tv/helix/streams?user_id='

TIME_INTERVAL = 60 # script executed every x seconds
RECENT_STATE = 1 # initial state

def get_access_token():
    req = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_SECRET}&grant_type=client_credentials")
    return json.loads(req.text)["access_token"]

def isOnline(twitch_channel_id):
    global TWITCH_OAUTH_TOKEN
    jData = None
    status = 1
    try:
        r = requests.get(TWITCH_USER_URL+twitch_channel_id, headers={"Client-Id": TWITCH_CLIENT_ID, "Authorization": TWITCH_OAUTH_TOKEN}, timeout=15)
        r.raise_for_status()
        jData = r.json()
        if jData['data'] == []:
            status = 1 # offline
        else:
            status = 0 # online
    except requests.exceptions.ConnectionError as cone:
        print("Connection Error:", cone)
    except requests.exceptions.Timeout as et:
        print("Timeout Error:", et)
    except requests.exceptions.RequestException as re:
        if "401" in str(re):
            TWITCH_OAUTH_TOKEN = 'Bearer '+get_access_token() # new token generation after old expired
        if re.response:
            if re.response.reason == 'Not Found' or re.response.reason == 'Unprocessable Entity':
                status = 2 # no streamer found
        print("Error message:", re)
    return status

def gameIdToGame(gameID):
    req = requests.get('https://api.twitch.tv/helix/games?id='+gameID, headers={"Client-ID": TWITCH_CLIENT_ID, "Authorization": TWITCH_OAUTH_TOKEN}, timeout=15)
    return json.loads(req.text)['data'][0]['name']

def getInfos(twitch_channel_id):
    infos = {'title':'', 'gameTitle':''}
    jData = None
    try:
        r = requests.get(TWITCH_USER_URL+twitch_channel_id, headers={"Client-Id": TWITCH_CLIENT_ID, "Authorization": TWITCH_OAUTH_TOKEN}, timeout=15)
        r.raise_for_status()
        jData = r.json()
    except requests.exceptions.ConnectionError as cone:
        print("Connection Error:", cone)
    except requests.exceptions.Timeout as et:
        print("Timeout Error:", et)
    except requests.exceptions.RequestException as re:
        print("Error message:", re)
    infos['title'] = jData['data'][0]['title']
    infos['gameTitle'] = gameIdToGame(jData['data'][0]['game_id'])
    return infos

while True:
    time.sleep(TIME_INTERVAL)
    status = isOnline(TWITCH_CHANNEL_ID)
    if not status and RECENT_STATE:
        infos = getInfos(TWITCH_CHANNEL_ID)
        webhook = Webhook.partial(DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
        webhook.send("I am live! Come watch me at : https://twitch.tv/"+TWITCH_CHANNEL +"\nTitle : "+infos['title']+"\nPlaying : "+infos['gameTitle'])
        RECENT_STATE = 0
    elif not (status or RECENT_STATE):
        continue
    else:
        RECENT_STATE = 1