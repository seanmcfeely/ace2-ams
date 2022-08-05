#!/usr/bin/env bash

# Exit if any command fails
set -e

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}

# Bring up the containers in TESTING mode so Vite loads the testing config
docker compose -f $COMPOSE_FILE up -d

# Wait for things to be ready
docker exec ace2-frontend bin/wait-for-gui.sh

# Run Cypress
docker exec -e VITE_TESTING_MODE=yes ace2-frontend curl http://ace2-ams:8080/login
docker exec -e VITE_TESTING_MODE=yes ace2-frontend echo "db_api"
docker exec -e VITE_TESTING_MODE=yes ace2-frontend curl http://db-api/api/ping
docker exec -e VITE_TESTING_MODE=yes ace2-frontend echo "gui_api"
docker exec -e VITE_TESTING_MODE=yes ace2-frontend curl http://gui-api/api/ping
#docker exec -e VITE_TESTING_MODE=yes ace2-frontend xvfb-run cypress run --e2e --headless --browser chrome --config-file "cypress.config.ts" --config video=false,screenshotOnRunFailure=false