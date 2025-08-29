> note: due to a limitation on the zrok free tier, the filebrowser part of this system isn't currently working. i'm working on a fix! in the meantime, it should be enough to get navidrome and slskd working.

# overview

this is a guide to setting up your own diy streaming server. it uses docker compose to combine a few open source solutions and put them together. you can run this on any old computer you have lying around with an internet connection. it should even run on a low-power computer like a raspberry pi. all the software is free.

## components

on your server:
* navidrome - this is the heart of your streaming server (https://www.navidrome.org/). it uses the subsonic protocol
* slskd - this is a soulseek instance that also runs on your streaming server, so you can download music from anywhere and it will be available for you to stream (https://github.com/slskd/slskd)
* filebrowser - a simple tool for you to upload music to your server from anywhere (https://filebrowser.org/)
* zrok - a reverse proxy to expose these servers to the public internet so you can access them (https://zrok.io/)

on your phone:
* a subsonic client for listening to your music (e.g. Amperfy on iOS, Symfonium on Android)
* slskd and fileuploader client URLs bookmarked in your browser so you can download and upload files from wherever

## setup
these directions are for a mac, but should be similar on any unix-based system. on windows, YMMV but the general principles still apply.

you'll need to download and install docker desktop - https://www.docker.com/products/docker-desktop/

then, you'll need to set up zrok:

```
# install zrok
brew install zrok

# set up a zrok account. this will open a browser where you login and get an auth token for the next step
zrok invite

# log into zrok with the auth token
zrok enable "$ZROK_AUTH_TOKEN"
```

### config
set up your .env with the names you want for your streaming and download servers. pick something unique that you think no one else would have used on zrok. here's what i used:

```
# .env
STREAMING_SERVER_NAME=ashidrome
DOWNLOAD_SERVER_NAME=ashiseek
UPLOAD_SERVER_NAME=ashiupload
```

also, replace the soulseek credentials with the ones you want to use. you don't need to create a soulseek account anywhere beforehand.

then, run setup.sh to get zrok set up:
```
./setup.sh
```

### docker
next, start all the docker containers:
```
./start.sh
```

### credentials

#### navidrome admin user
visit navidrome to set up your initial admin user at http://localhost:4533/app/#/login

#### filebrowser credentials
go to the docker desktop app and copy the randomly generated admin password from the filebrowser container logs. it will only be shown once!

### testing

you should also now be able to access your navidrome and slskd instances at the URLs generated based on your config file. for example, these are mine because my STREAMING_SERVER_NAME is ashidrome and my DOWNLOAD_SERVER_NAME is ashiseek and my UPLOAD_SERVER_NAME is ashiupload:
```
https://ashidrome.share.zrok.io
https://ashiseek.share.zrok.io
https://ashiupload.share.zrok.io
```

you can use the slskd credentials you added to your .env file, the navidrome credentials you created when you first opened it, and the filebrowser credentials you copied from the docker logs to log into each system.

## usage
the general idea is that you download music from soulseek (in my case, ashiseek.share.zrok.io) and it automatically goes into your navidrome library. so then you can listen to it on your phone from anywhere (i use the amperfy client on my iphone). if you purchase music from somewhere like bandcamp and want to upload it, then go to your fileupload server and it will automatically be added to your navidrome library as well.

### users
you can make multiple users with separate libraries and permissions. in my testing so far i have had multiple users but one shared library, and this seems to be the simplest way to share music but have your own playlists.

### sharing
navidrome is under active development. one of the features they're currently working on is sharing music from your library with people who don't have a user account on your server. keep an eye on this feature as it will hopefully improve! and give the team feedback if you have any. open source projects need our help! https://www.navidrome.org/docs/usage/sharing/

### settings
there are lots of settings that can be changed in all of these systems, and i encourage you to explore their own documentation. this guide is just an attempt to streamline setting them up to work together. for example, amperfy lets you decide if you want to stream the original file formats (e.g. high-quality but large FLACs) or transcode to a lower-bitrate MP3 for faster speeds. these are the kind of decisions that spotify and apple music make for you, but now that you have your own setup, you can make your own decisions!

## next steps
have you tried this? let me know where you got stuck! if you want help getting this set up for your household or community, please reach out. and also give feedback to the maintainers of the projects that i've built upon with this guide.

