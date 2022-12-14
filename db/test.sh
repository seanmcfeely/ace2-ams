#!/bin/bash

# Set up the variables
DB=${POSTGRES_DB:-ace}
USER=${POSTGRES_USER:-ace}
PASS=${POSTGRES_PASSWORD:-password}
DATABASE_URL=postgresql://$USER:$PASS@ace2-db:5432/$DB

# Remove the leading db/ and app/ from the command line argument (if they are there) so the path works inside the container.
NEW_PATH=${1#db/app/}
NEW_PATH=${NEW_PATH#app/}

# Make sure leftover containers from previous runs don't exist
echo "Removing leftover Docker containers"
docker rm -f ace2-db-crud > /dev/null 2>&1
docker rm -f ace2-db > /dev/null 2>&1
docker network rm ace2-db-net > /dev/null 2>&1

# Immediately exit with error status if any subsequent command fails
set -e

# Create a temporary network for the test containers
echo "Creating temporary Docker network"
docker network create ace2-db-net > /dev/null

# Build and run a temporary database container
echo "Creating temporary database container"
docker build -t ace2-db -f Dockerfile.database .
docker run -d --net ace2-db-net --name ace2-db -e POSTGRES_DB=$DB -e POSTGRES_USER=$USER -e POSTGRES_PASSWORD=$PASS ace2-db > /dev/null

# Build and run a temporary Python container to run the tests in
echo "Creating temporary Python container"
cd ..
docker build -t ace2-db-crud -f db/Dockerfile.crud .
docker run -d --net ace2-db-net --name ace2-db-crud -e DATABASE_URL=$DATABASE_URL ace2-db-crud > /dev/null

# Run the tests inside the Python container and capture its return code
echo "Running tests"
docker exec ace2-db-crud pytest -vv ${NEW_PATH:-db/tests/}
RETURN_CODE=$?

# Cleanup
echo "Cleaning up"
docker rm -f ace2-db-crud > /dev/null
docker rm -f ace2-db > /dev/null
docker network rm ace2-db-net > /dev/null

exit $RETURN_CODE