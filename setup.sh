#!/bin/sh

# grab env
source config.env

# set up zrok
zrok reserve public --unique-name "$STREAMING_SERVER_NAME" http:navidrome:4533
zrok reserve public --unique-name "$DOWNLOAD_SERVER_NAME" http:slskd:5030