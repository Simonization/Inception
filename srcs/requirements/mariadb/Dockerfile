FROM debian:bullseye

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y mariadb-server && \
    rm -rf /var/lib/apt/lists/*

COPY conf/50-server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf
COPY tools/setup_mariadb.sh /setup.sh
RUN chmod +x /setup.sh

ENTRYPOINT ["bash", "/setup.sh"]
