#!/bin/bash

# Function to print steps
print_step() {
    echo -e "\n\e[1;33m*** $1 ***\e[0m\n"
}

# Ensure the script exits on errors
set -e

print_step "Step 1: Stopping the Docker container"
docker-compose down

print_step "Step 2: Removing unused Docker images and containers"
docker system prune -f

print_step "Step 3: Displaying current Docker status"
docker ps -a

print_step "Deletion completed successfully!"
