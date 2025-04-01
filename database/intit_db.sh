#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Print each command for debugging
set -x



echo "Starting TimescaleDB setup process"

# 1. Start Docker containers from the docker-compose file
echo "Starting Docker containers"
docker-compose up -d

# 2. Wait for the database to be ready
echo "Waiting for TimescaleDB to be ready"
sleep 20  # Simple approach

echo "TimescaleDB is ready!"

echo "Install python packages"

# install necessary python packages using pip
pip install -r requirements.txt

echo "Packages are installed"

echo "Set-up timescale DB databse schema"
python3 db_setup.py

echo "Retrieve historical data to be loaded into DB"
python3 hist_ret.py

echo "Setup complete! Your TimescaleDB is ready to use."