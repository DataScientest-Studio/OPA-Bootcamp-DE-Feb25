#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Print each command for debugging
set -x

echo "Starting TimescaleDB setup process"

# get user input for host information
read -p "Please enter the hostname/address of your VM: " DB_NAME
#create and empty host.txt file
touch host.txt
# write infos
echo $DB_NAME > host.txt

# 1. Start Docker containers from the docker-compose file
echo "Starting Docker containers"
docker-compose up -d

# 2. Wait for the database to be ready
echo "Waiting for TimescaleDB to be ready"
sleep 10  # Simple approach

echo "TimescaleDB is ready!"

echo "Retrieve historical data to be loaded into DB"
python3 hist_ret.py

echo "Setup complete! Your TimescaleDB is ready to use."