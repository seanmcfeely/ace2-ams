#!/usr/bin/env bash

# Exit if any command fails
set -e

# Set up the variables
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}
FASTAPI_BASE=${FASTAPI_BASE:-tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim}

# Bring up the containers
docker compose -f $COMPOSE_FILE build --build-arg fastapi_base=$FASTAPI_BASE
docker compose -f $COMPOSE_FILE up -d

# Run Cypress
docker exec -e TZ=America/New_York -e CYPRESS_COVERAGE=true ace2-frontend xvfb-run cypress run --component --headless --browser chrome --config-file "cypress.config.ts" --config video=false,screenshotOnRunFailure=false
docker exec ace2-frontend npx nyc report --reporter=text-summary