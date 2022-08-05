#!/usr/bin/env bash

# Remove the leading frontend/ from the command line argument so the path works inside of the container.
TEST_FILE=${1#frontend/}

# Exit if any command fails
set -e

# Bring up the containers (if they aren't already)
docker compose up -d

docker exec -e VITE_BACKEND_URL=http://localhost:3000/api/ ace2-frontend npm run test:unit "$TEST_FILE"