FROM debian:bullseye

RUN apt-get update && apt-get install -y nginx openssl && \
    rm -rf /var/lib/apt/lists/*

RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default

COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY tools/setup_ssl.sh /setup.sh
RUN chmod +x /setup.sh

RUN chmod -R 755 /var/www/html && chown -R www-data:www-data /var/www/html

EXPOSE 443

ENTRYPOINT ["bash", "/setup.sh"]
