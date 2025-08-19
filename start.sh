#!/bin/sh

./setup.sh

docker compose -f 'docker-compose.yml' up -d --build