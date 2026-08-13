#!/bin/sh

chown -R 1000:1000 ./slskd_data ./music 2>/dev/null || true
docker compose -f 'docker-compose.yml' up -d --build