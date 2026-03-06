#!/bin/bash

echo "Starting MariaDB initialization..."

# Read passwords from Docker secrets
if [ -f /run/secrets/db_root_password ]; then
    SQL_ROOT_PASSWORD=$(cat /run/secrets/db_root_password)
fi
if [ -f /run/secrets/db_password ]; then
    SQL_PASSWORD=$(cat /run/secrets/db_password)
fi

# Validate required variables
if [ -z "$SQL_ROOT_PASSWORD" ] || [ -z "$SQL_DATABASE" ] || [ -z "$SQL_USER" ] || [ -z "$SQL_PASSWORD" ]; then
    echo "ERROR: Missing required environment variables or secrets."
    echo "Need: SQL_ROOT_PASSWORD, SQL_DATABASE, SQL_USER, SQL_PASSWORD"
    exit 1
fi

# Ensure run directory exists
mkdir -p /run/mysqld
chown mysql:mysql /run/mysqld

# Initialize data directory if empty
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo "Initializing MariaDB data directory..."
    mysql_install_db --user=mysql --datadir=/var/lib/mysql > /dev/null 2>&1
fi

# Start MariaDB temporarily for setup
mysqld_safe --skip-grant-tables &
TEMP_PID=$!

echo "Waiting for MariaDB to be ready..."
MAX_RETRIES=30
COUNT=0
while [ $COUNT -lt $MAX_RETRIES ]; do
    if mysqladmin ping -h"localhost" --silent 2>/dev/null; then
        echo "MariaDB is ready!"
        break
    fi
    echo "Waiting... attempt $((COUNT + 1))/$MAX_RETRIES"
    sleep 2
    COUNT=$((COUNT + 1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: MariaDB failed to start."
    exit 1
fi

echo "Configuring database and users..."

# Check if database already configured (idempotent)
DB_EXISTS=$(mysql -u root -e "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='${SQL_DATABASE}';" 2>/dev/null | grep -c "${SQL_DATABASE}")

if [ "$DB_EXISTS" -eq 0 ]; then
    mysql -u root <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '${SQL_ROOT_PASSWORD}';
CREATE DATABASE IF NOT EXISTS \`${SQL_DATABASE}\`;
CREATE USER IF NOT EXISTS '${SQL_USER}'@'%' IDENTIFIED BY '${SQL_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${SQL_DATABASE}\`.* TO '${SQL_USER}'@'%';
FLUSH PRIVILEGES;
EOF
    echo "Database configured!"
else
    echo "Database already exists, updating passwords..."
    mysql -u root <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '${SQL_ROOT_PASSWORD}';
ALTER USER IF EXISTS '${SQL_USER}'@'%' IDENTIFIED BY '${SQL_PASSWORD}';
FLUSH PRIVILEGES;
EOF
    echo "Passwords updated."
fi

# Shutdown temporary instance
mysqladmin -u root -p"${SQL_ROOT_PASSWORD}" shutdown 2>/dev/null
wait $TEMP_PID 2>/dev/null
sleep 2

echo "Starting MariaDB in foreground..."
exec mysqld_safe
