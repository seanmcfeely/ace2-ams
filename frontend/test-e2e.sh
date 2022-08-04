#!/usr/bin/env bash

# Exit if any command fails
set -e

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}

# Stop any running version of the GUI
bin/stop-dev-gui.sh

# Bring up the containers in TESTING mode so Vite loads the testing config
VITE_TESTING_MODE=yes docker compose -f $COMPOSE_FILE up -d

# Wait for things to be ready
docker exec ace2-frontend bin/wait-for-gui.sh

# Run Cypress
docker exec ace2-frontend xvfb-run cypress run --e2e --headless --browser chrome --config-file "cypress.config.ts" --config video=false,screenshotOnRunFailure=false