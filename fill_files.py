#!/usr/bin/env python3
import os

def write(path, content):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"OK: {path}")

write("srcs/.env", """\
DOMAIN_NAME=slangero.42.fr

SQL_ROOT_PASSWORD=R00tSecurePass42
SQL_DATABASE=wordpress
SQL_USER=slangero
SQL_PASSWORD=WpSecurePass42

WP_ADMIN_USER=superuser
WP_ADMIN_PASSWORD=Admin42secure
WP_ADMIN_EMAIL=admin@slangero.42.fr
WP_USER=slangero_wp
WP_USER_PASSWORD=User42secure
WP_USER_EMAIL=user@slangero.42.fr

SQL_DATA_PATH=/home/slangero/data/mysql
WP_DATA_PATH=/home/slangero/data/wordpress
""")

write("srcs/.env.example", """\
DOMAIN_NAME=login.42.fr
SQL_ROOT_PASSWORD=your_root_password
SQL_DATABASE=wordpress
SQL_USER=your_db_user
SQL_PASSWORD=your_db_password
WP_ADMIN_USER=your_wp_admin
WP_ADMIN_PASSWORD=your_wp_admin_password
WP_ADMIN_EMAIL=admin@login.42.fr
WP_USER=your_wp_user
WP_USER_PASSWORD=your_wp_user_password
WP_USER_EMAIL=user@login.42.fr
SQL_DATA_PATH=/home/login/data/mysql
WP_DATA_PATH=/home/login/data/wordpress
""")

write("srcs/requirements/nginx/Dockerfile", """\
FROM debian:bullseye

RUN apt-get update && apt-get install -y nginx openssl && \\
    rm -rf /var/lib/apt/lists/*

RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default

COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY tools/setup_ssl.sh /setup.sh
RUN chmod +x /setup.sh

RUN chmod -R 755 /var/www/html && chown -R www-data:www-data /var/www/html

EXPOSE 443

ENTRYPOINT ["bash", "/setup.sh"]
""")

write("srcs/requirements/nginx/conf/nginx.conf", """\
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 443 ssl http2;
        server_name slangero.42.fr www.slangero.42.fr;

        ssl_certificate /etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx.key;
        ssl_protocols TLSv1.2 TLSv1.3;

        root /var/www/html;
        index index.php index.html index.htm;

        location / {
            try_files $uri $uri/ /index.php?$args;
        }

        location ~ \\.php$ {
            fastcgi_split_path_info ^(.+\\.php)(/.+)$;
            fastcgi_pass wordpress:9000;
            fastcgi_index index.php;
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            fastcgi_param PATH_INFO $fastcgi_path_info;
        }

        location ~ /\\.ht {
            deny all;
        }
    }
}
""")

write("srcs/requirements/nginx/tools/setup_ssl.sh", """\
#!/bin/bash

echo "Setting up SSL certificates..."

if [ -z "$DOMAIN_NAME" ]; then
    echo "ERROR: Missing DOMAIN_NAME environment variable."
    exit 1
fi

mkdir -p /etc/nginx/ssl

if [ ! -f /etc/nginx/ssl/nginx.crt ]; then
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
        -keyout /etc/nginx/ssl/nginx.key \\
        -out /etc/nginx/ssl/nginx.crt \\
        -subj "/C=BE/ST=Brussels/L=Brussels/O=42School/OU=student/CN=${DOMAIN_NAME}"
    echo "SSL certificate generated."
else
    echo "SSL certificate already exists, skipping..."
fi

echo "Starting NGINX..."
exec nginx -g "daemon off;"
""")

write("srcs/requirements/mariadb/Dockerfile", """\
FROM debian:bullseye

RUN apt-get update && apt-get upgrade -y && \\
    apt-get install -y mariadb-server && \\
    rm -rf /var/lib/apt/lists/*

COPY conf/50-server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf
COPY tools/setup_mariadb.sh /setup.sh
RUN chmod +x /setup.sh

ENTRYPOINT ["bash", "/setup.sh"]
""")

write("srcs/requirements/mariadb/conf/50-server.cnf", """\
[mysqld]
user = mysql
pid-file = /run/mysqld/mysqld.pid
basedir = /usr
datadir = /var/lib/mysql
tmpdir = /tmp
lc-messages-dir = /usr/share/mysql
lc-messages = en_US
skip-external-locking
bind-address = 0.0.0.0
expire_logs_days = 10
character-set-server = utf8mb4
collation-server = utf8mb4_general_ci
""")

write("srcs/requirements/mariadb/tools/setup_mariadb.sh", """\
#!/bin/bash

echo "Starting MariaDB initialization..."

if [ -z "$SQL_ROOT_PASSWORD" ] || [ -z "$SQL_DATABASE" ] || [ -z "$SQL_USER" ] || [ -z "$SQL_PASSWORD" ]; then
    echo "ERROR: Missing required environment variables."
    exit 1
fi

service mariadb start

echo "Waiting for MariaDB to be ready..."
MAX_RETRIES=30
COUNT=0
while [ $COUNT -lt $MAX_RETRIES ]; do
    if mysqladmin ping -h"localhost" --silent; then
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

mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '${SQL_ROOT_PASSWORD}';
FLUSH PRIVILEGES;
EOF

mysql -u root -p"${SQL_ROOT_PASSWORD}" <<EOF
CREATE DATABASE IF NOT EXISTS \`${SQL_DATABASE}\`;
CREATE USER IF NOT EXISTS '${SQL_USER}'@'%' IDENTIFIED BY '${SQL_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${SQL_DATABASE}\`.* TO '${SQL_USER}'@'%';
FLUSH PRIVILEGES;
EOF

echo "Database configured!"

mysqladmin -u root -p"${SQL_ROOT_PASSWORD}" shutdown
sleep 2

echo "Starting MariaDB in foreground..."
exec mysqld_safe
""")

write("srcs/requirements/wordpress/Dockerfile", """\
FROM debian:bullseye

RUN apt-get update && apt-get upgrade -y && \\
    apt-get install -y wget php7.4-fpm php7.4-mysql mariadb-client && \\
    rm -rf /var/lib/apt/lists/*

RUN wget https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \\
    -O /usr/local/bin/wp && chmod +x /usr/local/bin/wp

COPY conf/www.conf /etc/php/7.4/fpm/pool.d/www.conf

RUN mkdir -p /var/www/html

COPY tools/setup_wordpress.sh /setup.sh
RUN chmod +x /setup.sh

EXPOSE 9000

WORKDIR /var/www/html

ENTRYPOINT ["bash", "/setup.sh"]
""")

write("srcs/requirements/wordpress/conf/www.conf", """\
[www]
user = www-data
group = www-data
listen = 0.0.0.0:9000
listen.owner = www-data
listen.group = www-data
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
""")

write("srcs/requirements/wordpress/tools/setup_wordpress.sh", """\
#!/bin/bash

echo "Starting WordPress installation..."

if [ -z "$SQL_DATABASE" ] || [ -z "$SQL_USER" ] || \\
   [ -z "$SQL_PASSWORD" ] || [ -z "$DOMAIN_NAME" ] || \\
   [ -z "$WP_ADMIN_USER" ] || [ -z "$WP_ADMIN_PASSWORD" ] || \\
   [ -z "$WP_ADMIN_EMAIL" ] || [ -z "$WP_USER" ] || \\
   [ -z "$WP_USER_EMAIL" ] || [ -z "$WP_USER_PASSWORD" ]; then
    echo "ERROR: Missing required environment variables."
    exit 1
fi

echo "Waiting for MariaDB..."
sleep 5

MAX_RETRIES=30
COUNT=0
while [ $COUNT -lt $MAX_RETRIES ]; do
    if mysqladmin ping -h"mariadb" -u"$SQL_USER" -p"$SQL_PASSWORD" --silent; then
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
    wp config create --allow-root \\
        --dbname="${SQL_DATABASE}" \\
        --dbuser="${SQL_USER}" \\
        --dbpass="${SQL_PASSWORD}" \\
        --dbhost="mariadb:3306" \\
        --path="/var/www/html/"

    echo "Installing WordPress..."
    wp core install --allow-root \\
        --url="${DOMAIN_NAME}" \\
        --title="Inception42" \\
        --admin_user="${WP_ADMIN_USER}" \\
        --admin_password="${WP_ADMIN_PASSWORD}" \\
        --admin_email="${WP_ADMIN_EMAIL}" \\
        --path="/var/www/html/"

    echo "Creating secondary user..."
    wp user create "${WP_USER}" "${WP_USER_EMAIL}" \\
        --user_pass="${WP_USER_PASSWORD}" \\
        --role=author \\
        --allow-root \\
        --path="/var/www/html/"
else
    echo "WordPress already installed, skipping."
fi

mkdir -p /run/php
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

echo "Starting PHP-FPM..."
exec php-fpm7.4 -F
""")

write("srcs/docker-compose.yml", """\
version: "3"

services:
  mariadb:
    build:
      context: ./requirements/mariadb
      dockerfile: Dockerfile
    container_name: mariadb
    env_file: .env
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      - inception
    restart: unless-stopped

  wordpress:
    build:
      context: ./requirements/wordpress
      dockerfile: Dockerfile
    container_name: wordpress
    env_file: .env
    volumes:
      - wordpress_data:/var/www/html
    networks:
      - inception
    depends_on:
      - mariadb
    restart: unless-stopped

  nginx:
    build:
      context: ./requirements/nginx
      dockerfile: Dockerfile
    container_name: nginx
    env_file: .env
    ports:
      - "443:443"
    volumes:
      - wordpress_data:/var/www/html
    networks:
      - inception
    depends_on:
      - wordpress
    restart: unless-stopped

volumes:
  mariadb_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${SQL_DATA_PATH}

  wordpress_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${WP_DATA_PATH}

networks:
  inception:
    driver: bridge
""")

write("Makefile", """\
all:
\t@bash run_docker.sh

clean:
\t@bash run_docker.sh --clean

fclean: clean

re:
\t@bash run_docker.sh --blank-start

.PHONY: all clean fclean re
""")

write("run_docker.sh", """\
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
    sudo docker compose -f srcs/docker-compose.yml down --volumes --remove-orphans
    sudo docker system prune -f
    sudo rm -rf "${SQL_DATA_PATH}"
    sudo rm -rf "${WP_DATA_PATH}"
    echo "Cleanup complete."
    if $CLEAN_ONLY; then
        exit 0
    fi
else
    echo "Continuing with existing data..."
    sudo docker compose -f srcs/docker-compose.yml down --remove-orphans
fi

if ! grep -q "${DOMAIN_NAME}" /etc/hosts; then
    echo "127.0.0.1 ${DOMAIN_NAME}" | sudo tee -a /etc/hosts
    echo "Added ${DOMAIN_NAME} to /etc/hosts"
else
    echo "${DOMAIN_NAME} already in /etc/hosts"
fi

mkdir -p "${SQL_DATA_PATH}"
mkdir -p "${WP_DATA_PATH}"

if $BLANK_START; then
    echo "Building images from scratch..."
    sudo docker compose -f srcs/docker-compose.yml build --no-cache
    sudo docker compose -f srcs/docker-compose.yml up
else
    sudo docker compose -f srcs/docker-compose.yml up --build
fi
""")

print("\nAll files written! Run: make re")
