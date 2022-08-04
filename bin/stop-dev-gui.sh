#!/usr/bin/env bash

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}

echo "STOPPING COMPOSE_FILE=$COMPOSE_FILE"

docker compose -f frontend/$COMPOSE_FILE down