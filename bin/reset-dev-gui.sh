#!/usr/bin/env bash

# Destroy the existing development GUI environment
docker compose -f frontend/docker-compose.yml down -v --remove-orphans

# Build the new development GUI environment
docker compose -f frontend/docker-compose.yml build

# Start the development GUI environment
docker compose -f frontend/docker-compose.yml up -d