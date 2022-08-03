#!/usr/bin/env bash

# Set up the variables
DB=${POSTGRES_DB:-ace}
USER=${POSTGRES_USER:-ace}
PASS=${POSTGRES_PASSWORD:-password}
DATABASE_URL=postgresql://$USER:$PASS@ace2-db-migration:5432/$DB
CURRENT_DIR=`pwd`
PARENT_DIR=`dirname "$CURRENT_DIR"`

# Make sure leftover containers from previous runs don't exist
echo "Removing leftover Docker containers"
docker rm -f ace2-db-crud-migration > /dev/null 2>&1
docker rm -f ace2-db-migration > /dev/null 2>&1
docker network rm ace2-db-migration-net > /dev/null 2>&1

# Immediately exit with error status if any subsequent command fails
set -e

# Create a temporary network for the test containers
echo "Creating temporary Docker network"
docker network create ace2-db-migration-net > /dev/null

# Build and run a temporary database container
echo "Creating temporary database container"
docker build -t ace2-db-migration -f Dockerfile.database .
docker run --rm -d --net ace2-db-migration-net --name ace2-db-migration -e POSTGRES_DB=$DB -e POSTGRES_USER=$USER -e POSTGRES_PASSWORD=$PASS ace2-db-migration > /dev/null

# Build and run a temporary Python container to build the migration
echo "Creating temporary Python container"
docker build -t ace2-db-crud-migration -f Dockerfile.crud .
docker run --rm -d --net ace2-db-migration-net --name ace2-db-crud-migration --volume=$CURRENT_DIR/app/:/app --volume=$PARENT_DIR/api_models:/app/api_models -e DATABASE_URL=$DATABASE_URL ace2-db-crud-migration > /dev/null

# Run the tests inside the Python container
echo "Applying current database schema"
docker exec ace2-db-crud-migration alembic upgrade head

# Build the new database migration inside the Python container
docker exec ace2-db-crud-migration alembic revision --autogenerate -m "$1"

# Cleanup
echo "Cleaning up"
docker rm -f ace2-db-crud-migration > /dev/null
docker rm -f ace2-db-migration > /dev/null
docker network rm ace2-db-migration-net > /dev/null
rmdir app/api_models
