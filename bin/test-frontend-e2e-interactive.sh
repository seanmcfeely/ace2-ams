#!/usr/bin/env bash

# Stop any running version of the GUI
bin/stop-dev-gui.sh

# Restart the GUI in TESTING mode so Vite loads the testing config
cd frontend/
VITE_TESTING_MODE=yes docker compose up -d

# Wait for things to be ready
docker exec ace2-frontend bin/wait-for-gui.sh

# Open up the local Cypress test runner
npx cypress open

# Restart the GUI in its default (non-TESTING) state
cd ..
bin/reset-dev-gui.sh