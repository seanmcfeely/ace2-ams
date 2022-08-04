#!/usr/bin/env bash

# Exit if any command fails
set -e

# Bring up the containers (if they aren't already)
docker compose up -d

# Run Cypress
docker exec -e TZ=America/New_York -e CYPRESS_COVERAGE=true ace2-frontend xvfb-run cypress run --component --headless --browser chrome --config-file "cypress.config.ts" --config video=false,screenshotOnRunFailure=false
docker exec ace2-frontend npx nyc report --reporter=text-summary