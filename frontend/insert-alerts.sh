#!/usr/bin/env bash

docker compose up -d
docker exec ace2-db-api-frontend python db/insert-alerts.py $@