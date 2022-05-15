# General
ditwibot -> Discord-Twitch-Bot
Self-hosting bot that posts messages in discord channel automatically.

# ditwibot
Checks if twitch stream is online via Twitch API. Tokens available at https://dev.twitch.tv/console
Discord Webhook and Tokens available at discord channel -> settings -> integration -> generate webhook
Twitch user id available via userID.py
```python ditwibot.py TWITCH_CHANNEL TWITCH_CHANNEL_ID TWITCH_CLIENT_ID TWITCH_SECRET DISCORD_WEBHOOK_ID DISCORD_WEBHOOK_TOKEN```

# oauthToken.py
Generates the oauthToken or authentication token for Twitch from client ID and secret. IMPORTANT! Necessary for using the twtich API! You can find both by creating a twitch account and a new application at https://dev.twitch.tv/console

```python oauthToken.py CLIENT_ID SECRET```

# userID.py
Generates the user Id of an existing Twitch channel. Necessary for some API calls.

```python userID.py USERNAME CLIENT_ID OAUTH_TOKEN```

Username can be extracted from channel URL. 

Example: ```https://www.twitch.tv/github``` 

```github``` would be the USERNAME
