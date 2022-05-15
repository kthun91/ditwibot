#!/usr/bin/env python3
# python oauthToken.py CLIENT_ID SECRET
import sys
import requests

URL = 'https://id.twitch.tv/oauth2/token'
CLIENT_ID = sys.argv[1]
SECRET =sys.argv[2]
try:
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = f'client_id={CLIENT_ID}&client_secret={SECRET}&grant_type=client_credentials'
    req = requests.post(URL, headers=headers, data=data ,timeout=15)
    req.raise_for_status()
    jData = req.json()
    print('OAUTH-Token: ' + jData['access_token'])
    print('expires in ' + str(float(jData['expires_in'])/86400) + ' days')
    print('token type: ' + jData['token_type'])
except requests.exceptions.ConnectionError as cone:
        print("Connection Error:", cone)
except requests.exceptions.Timeout as et:
        print("Timeout Error:", et)
except requests.exceptions.RequestException as re:
        print("Error message:", re)
