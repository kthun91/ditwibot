#!/usr/bin/env python3
# python userID.py USERNAME CLIENT_ID OAUTH_TOKEN
import sys
import requests

URL = 'https://api.twitch.tv/helix/users?login='+sys.argv[1]

try:
    headers = {'Client-Id': sys.argv[2], 'Authorization': 'Bearer '+sys.argv[3]}
    req = requests.get(URL, headers=headers, timeout=15)
    req.raise_for_status()
    jData = req.json()
    print(jData['data'][0]['id'])
except requests.exceptions.ConnectionError as cone:
        print("Connection Error:", cone)
except requests.exceptions.Timeout as et:
        print("Timeout Error:", et)
except requests.exceptions.RequestException as re:
        print("Error message:", re)
