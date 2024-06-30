#!/bin/bash

mv sample.env .env

# Function to print steps
print_step() {
    echo -e "\n\e[1;33m*** $1 ***\e[0m\n"
}

# Ensure the script exits on errors
set -e

print_step "Step 1: Building the Docker image"
docker-compose build

print_step "Step 2: Bringing up the Docker container"
docker-compose up -d

print_step "Step 3: Displaying running containers"
docker ps

print_step "Deployment completed successfully!"
