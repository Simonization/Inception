#!/bin/bash

echo "Launching the project..."

BLANK_START=false
CLEAN_ONLY=false

if [[ "$1" == "--clean" ]]; then
    CLEAN_ONLY=true
fi

if [[ "$1" == "--blank-start" ]]; then
    BLANK_START=true
fi

sed -i "s|/home/[^/]*/data/|/home/$USER/data/|g" srcs/.env

if [ ! -f srcs/.env ]; then
    echo "ERROR: srcs/.env file not found."
    exit 1
fi

source srcs/.env

if $BLANK_START || $CLEAN_ONLY; then
    if $CLEAN_ONLY; then
        echo "Cleaning up environment..."
    else
        echo "Starting fresh with clean volumes..."
    fi
    docker compose -f srcs/docker-compose.yml down --volumes --remove-orphans
    docker system prune -f
    rm -rf "${SQL_DATA_PATH}"
    rm -rf "${WP_DATA_PATH}"
    echo "Cleanup complete."
    if $CLEAN_ONLY; then
        exit 0
    fi
else
    echo "Continuing with existing data..."
    docker compose -f srcs/docker-compose.yml down --remove-orphans
fi

if ! grep -q "${DOMAIN_NAME}" /etc/hosts; then
    echo "WARNING: ${DOMAIN_NAME} not found in /etc/hosts"
    echo "Please ask an admin or run manually:"
    echo "  echo '127.0.0.1 ${DOMAIN_NAME}' | sudo tee -a /etc/hosts"
else
    echo "${DOMAIN_NAME} already in /etc/hosts - OK"
fi

mkdir -p "${SQL_DATA_PATH}"
mkdir -p "${WP_DATA_PATH}"

if $BLANK_START; then
    echo "Building images from scratch..."
    docker compose -f srcs/docker-compose.yml build --no-cache
    docker compose -f srcs/docker-compose.yml up
else
    docker compose -f srcs/docker-compose.yml up --build
fi
