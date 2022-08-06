#!/usr/bin/env bash

# Exit if any command fails
set -e

# Set up the variables
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}
FASTAPI_BASE=${FASTAPI_BASE:-tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim}

# Bring up the containers
docker compose -f $COMPOSE_FILE build --build-arg fastapi_base=$FASTAPI_BASE
docker compose -f $COMPOSE_FILE up -d

# Wait for things to be ready
docker exec ace2-frontend bin/wait-for-gui.sh

# Run Cypress
docker exec -e VITE_TESTING_MODE=yes ace2-frontend xvfb-run cypress run --e2e --headless --browser chrome --config-file "cypress.config.ts" --config video=false,screenshotOnRunFailure=false