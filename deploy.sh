#!/bin/bash
set -e

echo "=== System Update & Prerequisites ==="
sudo apt-get update && sudo apt-get install -y git curl apt-transport-https ca-certificates software-properties-common

if ! command -v docker &> /dev/null; then
    curl -fsSL https://docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

echo "=== Configuring SWAP Memory (1GB) ==="
if [ ! -f /swapfile ]; then
    sudo dd if=/dev/zero of=/swapfile bs=1M count=1024
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

ENV_PATH=$(pwd)/.env
if [ ! -f "$ENV_PATH" ]; then
    echo "Error: Please create a .env file in the current directory before running the script."
    exit 1
fi

echo "=== Cloning Git Repository ==="
rm -rf booking-service-api
git clone https://github.com/illaay/booking-service-api.git
cd booking-service-api

cp "$ENV_PATH" .env

echo "=== Docker Compose Orchestration ==="
sudo docker compose down -v || true
sudo docker compose build --no-cache
sudo docker compose up -d db redis

echo "=== Awaiting database readiness ==="
sleep 7

sudo docker compose run --rm web python manage.py migrate
sudo docker compose run --rm web python manage.py collectstatic --noinput
sudo docker compose run --rm web python manage.py seed_data

sudo docker compose up -d

echo "Successful!"
