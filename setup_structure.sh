#!/bin/bash
mkdir -p srcs/requirements/nginx/{conf,tools}
mkdir -p srcs/requirements/mariadb/{conf,tools}
mkdir -p srcs/requirements/wordpress/{conf,tools}
mkdir -p secrets
touch Makefile srcs/docker-compose.yml srcs/.env srcs/.env.example README.md USER_DOC.md DEV_DOC.md run_docker.sh
touch srcs/requirements/nginx/Dockerfile srcs/requirements/nginx/.dockerignore
touch srcs/requirements/nginx/conf/nginx.conf srcs/requirements/nginx/tools/setup_ssl.sh
touch srcs/requirements/mariadb/Dockerfile srcs/requirements/mariadb/.dockerignore
touch srcs/requirements/mariadb/conf/50-server.cnf srcs/requirements/mariadb/tools/setup_mariadb.sh
touch srcs/requirements/wordpress/Dockerfile srcs/requirements/wordpress/.dockerignore
touch srcs/requirements/wordpress/conf/www.conf srcs/requirements/wordpress/tools/setup_wordpress.sh
touch secrets/credentials.txt secrets/db_password.txt secrets/db_root_password.txt
echo -e "srcs/.env\nsecrets/" > .gitignore
echo "✅ Done!"




