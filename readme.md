first, you'll need to set up zrok:

```
# install zrok
brew install zrok

# set up zrok account. this will open a browser where you login and get an auth token for the next step
zrok invite

# log into zrok with the auth token
zrok enable "$ZROK_AUTH_TOKEN"
```

set up your .env with the names you want for your streaming and download servers. they must be globally unique. example:

```
# .env
STREAMING_SERVER_NAME=ashidrome
DOWNLOAD_SERVER_NAME=ashiseek
```


