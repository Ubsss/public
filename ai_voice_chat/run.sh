#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

############################################################
# run docker-compose
############################################################

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Error: Docker is not installed or not in PATH."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null
then
    echo "Error: Docker does not appear to be running."
    exit 1
fi

# Check if a docker-compose file exists
if [[ ! -f "docker-compose.yml" && ! -f "docker-compose.yaml" ]]; then
    echo "Error: No docker-compose.yml or docker-compose.yaml found in current directory."
    exit 1
fi

# Run docker-compose in detached mode
echo "Starting Docker containers via docker-compose..."
docker-compose up -d