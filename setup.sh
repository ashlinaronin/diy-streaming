#!/bin/sh

# grab env
source config.env

# reserve public shares for your servers so they can have stable URLs
zrok reserve public --unique-name "$STREAMING_SERVER_NAME" http://localhost:4533
zrok reserve public --unique-name "$DOWNLOAD_SERVER_NAME" http://localhost:5030