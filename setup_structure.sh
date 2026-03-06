#!/bin/bash
# Setup script for Inception project
# Run this on a fresh clone to generate .env and secrets

USER_LOGIN="${USER}"

# Generate srcs/.env if missing
if [ ! -f srcs/.env ]; then
    cat > srcs/.env << EOF
DOMAIN_NAME=${USER_LOGIN}.42.fr
SQL_DATA_PATH=/home/${USER_LOGIN}/data/mariadb
WP_DATA_PATH=/home/${USER_LOGIN}/data/wordpress
SQL_DATABASE=wordpress
SQL_USER=wpuser
WP_TITLE=Inception
WP_ADMIN_USER=superuser
WP_ADMIN_EMAIL=superuser@${USER_LOGIN}.42.fr
WP_USER=${USER_LOGIN}
WP_USER_EMAIL=${USER_LOGIN}@${USER_LOGIN}.42.fr
EOF
    echo "Created srcs/.env"
else
    echo "srcs/.env already exists, skipping"
fi

# Generate secrets if missing
mkdir -p secrets
if [ ! -s secrets/db_password.txt ]; then
    echo "dbpass42" > secrets/db_password.txt
    echo "Created secrets/db_password.txt"
fi
if [ ! -s secrets/db_root_password.txt ]; then
    echo "rootpass42" > secrets/db_root_password.txt
    echo "Created secrets/db_root_password.txt"
fi
if [ ! -s secrets/credentials.txt ]; then
    cat > secrets/credentials.txt << EOF
WP_ADMIN_PASSWORD=adminpass42
WP_USER_PASSWORD=userpass42
EOF
    echo "Created secrets/credentials.txt"
fi

echo "Setup complete! You can now run: make re"




