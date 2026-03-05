#!/bin/bash

echo "Setting up SSL certificates..."

if [ -z "$DOMAIN_NAME" ]; then
    echo "ERROR: Missing DOMAIN_NAME environment variable."
    exit 1
fi

mkdir -p /etc/nginx/ssl

if [ ! -f /etc/nginx/ssl/nginx.crt ]; then
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/nginx.key \
        -out /etc/nginx/ssl/nginx.crt \
        -subj "/C=BE/ST=Brussels/L=Brussels/O=42School/OU=student/CN=${DOMAIN_NAME}"
    echo "SSL certificate generated."
else
    echo "SSL certificate already exists, skipping..."
fi

echo "Starting NGINX..."
exec nginx -g "daemon off;"
