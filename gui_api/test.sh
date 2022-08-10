#!/bin/bash

# Set up the variables
FASTAPI_BASE=${FASTAPI_BASE:-tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim}

# Remove the leading gui_api/ and app/ from the command line argument (if they are there) so the path works inside the container.
NEW_PATH=${1#gui_api/}
NEW_PATH=${NEW_PATH#app/}

# Make sure leftover containers from previous runs don't exist
echo "Removing leftover Docker containers"
docker rm -f ace2-gui-api > /dev/null 2>&1

# Immediately exit with error status if any subsequent command fails
set -e

# Build and run a temporary Python container to run the tests in
echo "Creating temporary Python container"
cd ..
docker build --build-arg fastapi_base=$FASTAPI_BASE -t ace2-gui-api -f gui_api/Dockerfile .
docker run -d --name ace2-gui-api -e DATABASE_API_URL=http://db-api/api -e COOKIES_SECURE=no ace2-gui-api > /dev/null

# Run the tests inside the Python container and capture its return code
echo "Running tests"
docker exec ace2-gui-api pytest -vv ${NEW_PATH:-tests/}
RETURN_CODE=$?

# Cleanup
echo "Cleaning up"
docker rm -f ace2-gui-api > /dev/null

exit $RETURN_CODE