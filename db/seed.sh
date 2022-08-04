#!/usr/bin/env bash

# Make sure leftover containers from previous runs don't exist
echo "Removing leftover Docker containers"
docker rm -f ace2-db-crud > /dev/null 2>&1

# Immediately exit with error status if any subsequent command fails
set -e

# Build and run a temporary Python container to run the schema upgrade
echo "Creating temporary Python container"
cd ..
docker build -t ace2-db-crud -f db/Dockerfile.crud .
docker run -d --name ace2-db-crud -e DATABASE_URL=$DATABASE_URL ace2-db-crud > /dev/null

# Seed the database inside the Python container
echo "Applying current database schema"
docker exec ace2-db-crud python db/seed.py

# Cleanup
echo "Cleaning up"
docker rm -f ace2-db-crud > /dev/null