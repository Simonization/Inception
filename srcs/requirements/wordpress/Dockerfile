FROM debian:bullseye

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y wget php7.4-fpm php7.4-mysql mariadb-client && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    -O /usr/local/bin/wp && chmod +x /usr/local/bin/wp

COPY conf/www.conf /etc/php/7.4/fpm/pool.d/www.conf

RUN mkdir -p /var/www/html

COPY tools/setup_wordpress.sh /setup.sh
RUN chmod +x /setup.sh

EXPOSE 9000

WORKDIR /var/www/html

ENTRYPOINT ["bash", "/setup.sh"]
