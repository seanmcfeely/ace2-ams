#!/usr/bin/env bash

# Exit if any command fails
set -e

# Bring up the containers (if they aren't already)
docker compose up -d

# Run the tests with coverage
docker exec -e VITE_TESTING=yes ace2-frontend npm run test:coverage