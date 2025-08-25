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


next, start all the docker containers:
```
docker compose -f docker-compose.yml' up -d --build
```

visit navidrome to set up your initial admin user at http://localhost:4533/app/#/login

you should also now be able to access your navidrome and slskd instances at the URLs generated based on your config file. for examplem, these are mine because my STREAMING_SERVER_NAME is ashidrome and my DOWNLOAD_SERVER_NAME is ashiseek:
```
https://ashidrome.share.zrok.io
https://ashiseek.share.zrok.io
```
