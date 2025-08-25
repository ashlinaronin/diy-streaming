# overview

## components

## setup

### config

### credentials

### testing

## usage

### downloading w/ soulseek

### uploading (bandcamp, etc)



## next steps



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
UPLOAD_SERVER_NAME=ashiupload
```


next, start all the docker containers:
```
docker compose -f docker-compose.yml' up -d --build
```

visit navidrome to set up your initial admin user at http://localhost:4533/app/#/login

you should also now be able to access your navidrome and slskd instances at the URLs generated based on your config file. for examplem, these are mine because my STREAMING_SERVER_NAME is ashidrome and my DOWNLOAD_SERVER_NAME is ashiseek and my UPLOAD_SERVER_NAME is ashiupload:
```
https://ashidrome.share.zrok.io
https://ashiseek.share.zrok.io
https://ashiupload.share.zrok.io
```

# check on filebrowser
go to docker desktop and copy the randomly generated admin password from the filebrowser container logs. it will only be shown once!

then navigate to http://localhost:8080 and enter username `admin` and the password you copied.
