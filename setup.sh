#!/bin/sh

# grab env
source .env

# reserve public shares for your servers so they can have stable URLs
zrok reserve public --unique-name "$STREAMING_SERVER_NAME" http://localhost:4533
zrok reserve public --unique-name "$DOWNLOAD_SERVER_NAME" http://localhost:5030

# unfortunately only two are allowed in free account
#zrok reserve public --unique-name "$UPLOAD_SERVER_NAME" http://localhost:8080