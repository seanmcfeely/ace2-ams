#!/usr/bin/env bash

# Make sure a migration name was supplied
if [ "$#" -ne 1 ]
then
  echo "Usage: revision.sh \"Name of migration\""
  exit 1
fi

# Set up the variables
DB=${POSTGRES_DB:-ace}
USER=${POSTGRES_USER:-ace}
PASS=${POSTGRES_PASSWORD:-password}
DATABASE_URL=postgresql://$USER:$PASS@ace2-db:5432/$DB
CURRENT_DIR=`pwd`

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
docker run --rm -d --net ace2-db-net --name ace2-db -e POSTGRES_DB=$DB -e POSTGRES_USER=$USER -e POSTGRES_PASSWORD=$PASS ace2-db > /dev/null

# Build and run a temporary Python container to build the migration
echo "Creating temporary Python container"
cd ..
docker build -t ace2-db-crud -f db/Dockerfile.crud .
docker run -d --net ace2-db-net --name ace2-db-crud --volume=$CURRENT_DIR/app/db/migrations/:/app/db/migrations -e DATABASE_URL=$DATABASE_URL ace2-db-crud > /dev/null

# Upgrade the database schema inside the Python container
echo "Applying current database schema"
docker exec ace2-db-crud alembic -c db/alembic.ini upgrade head

# Build the new database migration inside the Python container
docker exec ace2-db-crud alembic -c db/alembic.ini revision --autogenerate -m "$1"

# Cleanup
echo "Cleaning up"
docker rm -f ace2-db-crud > /dev/null
docker rm -f ace2-db > /dev/null
docker network rm ace2-db-net > /dev/null