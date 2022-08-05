#!/usr/bin/env bash

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}

docker compose -f frontend/$COMPOSE_FILE down