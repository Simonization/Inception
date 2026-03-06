#!/bin/bash

echo "Starting WordPress installation..."

# Read passwords from Docker secrets
if [ -f /run/secrets/db_password ]; then
    SQL_PASSWORD=$(cat /run/secrets/db_password)
fi
if [ -f /run/secrets/credentials ]; then
    source /run/secrets/credentials
fi

# Validate required variables
if [ -z "$SQL_DATABASE" ] || [ -z "$SQL_USER" ] || \
   [ -z "$SQL_PASSWORD" ] || [ -z "$DOMAIN_NAME" ] || \
   [ -z "$WP_ADMIN_USER" ] || [ -z "$WP_ADMIN_PASSWORD" ] || \
   [ -z "$WP_ADMIN_EMAIL" ] || [ -z "$WP_USER" ] || \
   [ -z "$WP_USER_EMAIL" ] || [ -z "$WP_USER_PASSWORD" ]; then
    echo "ERROR: Missing required environment variables or secrets."
    exit 1
fi

echo "Waiting for MariaDB..."
MAX_RETRIES=30
COUNT=0
while [ $COUNT -lt $MAX_RETRIES ]; do
    if mysqladmin ping -h"mariadb" -u"$SQL_USER" -p"$SQL_PASSWORD" --silent 2>/dev/null; then
        echo "MariaDB is ready!"
        break
    fi
    echo "Waiting... attempt $((COUNT + 1))/$MAX_RETRIES"
    sleep 2
    COUNT=$((COUNT + 1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Could not connect to MariaDB."
    exit 1
fi

if [ ! -f /var/www/html/wp-config.php ]; then
    echo "Downloading WordPress..."
    wp core download --version=6.0 --locale=en_US --allow-root

    echo "Creating wp-config.php..."
    wp config create --allow-root \
        --dbname="${SQL_DATABASE}" \
        --dbuser="${SQL_USER}" \
        --dbpass="${SQL_PASSWORD}" \
        --dbhost="mariadb:3306" \
        --path="/var/www/html/"

    echo "Installing WordPress..."
    wp core install --allow-root \
        --url="https://${DOMAIN_NAME}" \
        --title="Inception42" \
        --admin_user="${WP_ADMIN_USER}" \
        --admin_password="${WP_ADMIN_PASSWORD}" \
        --admin_email="${WP_ADMIN_EMAIL}" \
        --path="/var/www/html/"

    echo "Creating secondary user ${WP_USER}..."
    wp user create "${WP_USER}" "${WP_USER_EMAIL}" \
        --user_pass="${WP_USER_PASSWORD}" \
        --role=author \
        --allow-root \
        --path="/var/www/html/"
else
    echo "WordPress already installed, skipping."
fi

mkdir -p /run/php
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

echo "Starting PHP-FPM..."
exec php-fpm7.4 -F
