# ditwibot

under construction

# oauthToken.py
Generates the oauthToken or authentication token for twitch from client ID and secret. IMPORTANT! Neccesary for using the twtich API! You can find both by creating a twitch account and a new application at https://dev.twitch.tv/console
```python oauthToken.py CLIENT_ID SECRET```

# userID.py
Generates the user Id of an existing twitch channel. Neccesary for some API calls.
```python userID.py USERNAME CLIENT_ID OAUTH_TOKEN```

Username can be extracted from channel URL. 
Example: ```https://www.twitch.tv/github``` 
```github``` would be the USERNAME
