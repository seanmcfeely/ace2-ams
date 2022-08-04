#!/usr/bin/env bash

# Exit if any command fails
set -e

# Bring up the containers (if they aren't already)
docker compose up -d

# Wait for things to be ready
docker exec ace2-frontend bin/wait-for-gui.sh

# Run Cypress
docker exec ace2-frontend xvfb-run cypress run --e2e --headless --browser chrome --config-file "cypress.config.ts" --config video=false,screenshotOnRunFailure=false