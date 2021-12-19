#!/usr/bin/env bash

# Load the environment variables for the dev containers
ACE2_ENV_PATH="$HOME/.ace2.env"
set -a
source "$ACE2_ENV_PATH"
set +a

docker-compose up -d
docker exec -e SQL_ECHO=no ace2-ams-api python insert-alerts.py backend/app/tests/alerts/small.json
docker exec ace2-ams-gui npx cypress run --headless
