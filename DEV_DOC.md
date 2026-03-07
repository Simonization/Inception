# Developer Documentation — Inception

## Setting Up the Environment from Scratch

### Prerequisites

- Docker Engine (20.10+)
- Docker Compose (v2)
- `openssl` (for SSL certificate generation, handled automatically inside the NGINX container)
- Access to modify `/etc/hosts` or have `slangero.42.fr` already pointing to `127.0.0.1`

### Step 1: Clone the repository

```bash
git clone <repo-url>
cd Inception
```

### Step 2: Configure the domain

Ensure your machine resolves `slangero.42.fr` to localhost:

```bash
grep slangero.42.fr /etc/hosts
```

If not present, add it (requires admin privileges):

```bash
echo "127.0.0.1 slangero.42.fr" | sudo tee -a /etc/hosts
```

At 42 school machines without sudo, ask an admin or check if it's already configured.

### Step 3: Create the secrets

The `secrets/` directory is gitignored. You must create these files locally:

```bash
echo "YourDbPassword" > secrets/db_password.txt
echo "YourRootDbPassword" > secrets/db_root_password.txt
printf "WP_ADMIN_PASSWORD=YourAdminPass\nWP_USER_PASSWORD=YourUserPass\n" > secrets/credentials.txt
```

Each file must end with a newline and contain only the password value (for `db_password.txt` and `db_root_password.txt`) or key=value pairs (for `credentials.txt`).

### Step 4: Review the .env file

`srcs/.env` contains non-sensitive configuration. It is also gitignored. The `setup_structure.sh` script generates it with default values if it does not exist. The `run_docker.sh` script automatically updates the data paths to match the current `$USER`.

## Building and Launching

### Using the Makefile

| Command | What it does |
|---------|-------------|
| `make` | `docker compose up --build` — incremental build + start |
| `make clean` | `docker compose down --volumes` + remove data dirs + prune |
| `make fclean` | `make clean` + remove all Docker images + full system prune |
| `make re` | `make fclean` + rebuild from scratch with `--no-cache` |

### What `run_docker.sh` does

The Makefile delegates to `run_docker.sh`, which:

1. Updates `srcs/.env` with the current user's home directory
2. Sources `srcs/.env` for variable expansion
3. Depending on the flag (`--clean`, `--blank-start`, or none):
   - Tears down existing containers and optionally removes volumes/data
   - Or just stops existing containers before restarting
4. Checks `/etc/hosts` for the domain entry (warns if missing)
5. Creates the host data directories (`~/data/mysql`, `~/data/wordpress`)
6. Builds and starts the stack

### Manual Docker Compose commands

If you prefer to run commands directly:

```bash
# Build all images
docker compose -f srcs/docker-compose.yml build

# Start in foreground (see logs)
docker compose -f srcs/docker-compose.yml up

# Start in background
docker compose -f srcs/docker-compose.yml up -d

# Stop
docker compose -f srcs/docker-compose.yml down

# Stop and remove volumes
docker compose -f srcs/docker-compose.yml down --volumes
```

## Managing Containers and Volumes

### Useful container commands

```bash
# List running containers
docker ps

# View logs (follow mode)
docker logs -f nginx
docker logs -f wordpress
docker logs -f mariadb

# Open a shell inside a container
docker exec -it nginx bash
docker exec -it wordpress bash
docker exec -it mariadb bash

# Inspect a container's config
docker inspect nginx

# Check container restart policy
docker inspect --format='{{.HostConfig.RestartPolicy.Name}}' nginx
```

### Volume management

```bash
# List all volumes
docker volume ls

# Inspect a volume
docker volume inspect srcs_mariadb_data
docker volume inspect srcs_wordpress_data

# Remove unused volumes (careful!)
docker volume prune
```

### Network inspection

```bash
# List networks
docker network ls

# Inspect the inception network
docker network inspect srcs_inception

# Verify container connectivity
# WordPress can reach MariaDB (mysql client is installed for WP)
docker exec wordpress wp db check --path=/var/www/html

# NGINX can reach WordPress (it proxies PHP-FPM on port 9000)
# The fact that the website works IS the proof

```

## Data Storage and Persistence

### Where data lives

Data is stored on the host machine under `/home/slangero/data/`:

| Host path | Container mount | Service | Content |
|-----------|----------------|---------|---------|
| `/home/slangero/data/mysql` | `/var/lib/mysql` | MariaDB | Database files |
| `/home/slangero/data/wordpress` | `/var/www/html` | WordPress + NGINX | WordPress PHP files, uploads, wp-config.php |

Both paths are configured as Docker named volumes with the `local` driver and `bind` driver options in `docker-compose.yml`. This means Docker manages them as named volumes while the actual data resides at the specified host paths.

### How persistence works

- When you run `make` (or `docker compose up`), containers mount these directories. Any data written inside the container to `/var/lib/mysql` or `/var/www/html` is actually written to the host paths.
- When you run `make clean`, the `run_docker.sh` script removes the host directories entirely, so all data is lost.
- When you run `make` after `make clean` (without `make re`), the directories are recreated empty, and the entrypoint scripts detect the absence of data and run first-time initialization.

### WordPress file sharing

The `wordpress_data` volume is shared between the WordPress and NGINX containers. WordPress writes PHP files to `/var/www/html`, and NGINX reads them from the same path to serve static assets and forward PHP requests.

## Project File Structure

```
Inception/
├── Makefile                           # Build targets (all, clean, fclean, re)
├── run_docker.sh                      # Orchestration script
├── README.md                          # Project overview
├── USER_DOC.md                        # User documentation
├── DEV_DOC.md                         # Developer documentation (this file)
├── PLAN.md                            # Development plan
├── secrets/                           # Gitignored — password files
│   ├── db_password.txt
│   ├── db_root_password.txt
│   └── credentials.txt
└── srcs/
    ├── .env                           # Gitignored — generated by setup_structure.sh
    ├── docker-compose.yml             # Service definitions
    └── requirements/
        ├── nginx/
        │   ├── Dockerfile
        │   ├── .dockerignore
        │   ├── conf/nginx.conf        # NGINX server config (SSL, FastCGI)
        │   └── tools/setup_ssl.sh     # Generates SSL cert + starts NGINX
        ├── mariadb/
        │   ├── Dockerfile
        │   ├── .dockerignore
        │   ├── conf/50-server.cnf     # MariaDB server config
        │   └── tools/setup_mariadb.sh # Initializes DB + users + starts MariaDB
        └── wordpress/
            ├── Dockerfile
            ├── .dockerignore
            ├── conf/www.conf          # PHP-FPM pool config
            └── tools/setup_wordpress.sh # Downloads WP, configures, starts PHP-FPM
```

---

## Subject Requirements Guide


### PART 1 — Docker Concepts (docker-compose.yml)

#### Dockerfiles vs Volumes vs Networks

**Dockerfiles — "The Blueprint"**

```yaml
build:
  context: ./requirements/mariadb
  dockerfile: Dockerfile
```

A Dockerfile is a recipe: what base OS, what packages to install, what files to copy, what command to run. Think of it as an **apartment blueprint** — the Dockerfile describes how to build the apartment (image). Running that image gives you a **container** (the actual apartment).

**Volumes — "Persistent Storage"**

```yaml
volumes:
  - mariadb_data:/var/lib/mysql
```

Containers are ephemeral — when they stop, everything inside is lost. Volumes mount a path from the host machine into the container. So data survives container restarts and rebuilds. Think of it as a **USB drive** plugged into the container.

Note: both `nginx` and `wordpress` share the same `wordpress_data` volume — that is how nginx can serve PHP files that WordPress wrote.

**Networks — "Private LAN"**

```yaml
networks:
  inception:
    driver: bridge
```

All three services are on the `inception` network. They can talk to each other by container name (e.g., WordPress connects to `mariadb` as a hostname). Only nginx exposes port 443 to the outside. MariaDB and WordPress are invisible externally. Think of it as an **office building** — nginx is the public reception, the rest are internal offices.

#### Why `version: "3.8"`?

The `version` field tells Docker Compose which file format to use. Version 3.8 supports the `secrets` syntax used in this project. Modern Docker Compose v2 (the `docker compose` command without hyphen) actually ignores this field, but keeping it explicit is good practice.

You **can** change it:
- `3.9` or higher — works fine, backwards-compatible
- `3.0` to `3.4` — breaks, because `secrets:` at service level was not supported
- `2.x` — breaks, completely different secrets syntax
- Remove the line entirely — modern Docker Compose v2 handles it, older versions will error

---

### PART 2 — Live WordPress Demo

**Goal:** Show a working WordPress site with login, comments, and public visibility.

1. Open browser: `https://slangero.42.fr`
2. Accept the SSL warning (self-signed cert, generated at container startup by `setup_ssl.sh`)
3. Go to `https://slangero.42.fr/wp-login.php`, login as admin
4. Open any post, add a comment, publish it
5. Log out, revisit the post — the comment is visible without login

---

### PART 3 — WordPress Container Checks

**"Check there is a Dockerfile"**

```bash
cat srcs/requirements/wordpress/Dockerfile
```

Point out: base image is `debian:bullseye`, installs `php7.4-fpm` only — **no nginx in this container**.

**"Check there is a volume"**

```bash
docker inspect wordpress | grep -A 10 Mounts
```

Shows `wordpress_data` is mounted at `/var/www/html`.

**"Check with docker ps / ls"**

```bash
docker ps
docker volume ls
```

---

### PART 4 — MariaDB Container Checks

**"Check the Dockerfile"**

```bash
cat srcs/requirements/mariadb/Dockerfile
```

Point out: `debian:bullseye`, installs `mariadb-server` only — no nginx.

**"Check there is no nginx in the file"**

The corrector means no nginx installed in the MariaDB container:

```bash
docker exec mariadb which nginx   # should fail — nginx not installed
```

**"How to connect to the DB" — key commands:**

```bash
# Connect as the WordPress database user
docker exec -it mariadb mysql -u wpuser -p wordpress

# Or connect as root
docker exec -it mariadb mysql -u root -p
```

Then show the database exists:

```sql
SHOW DATABASES;
USE wordpress;
SHOW TABLES;
```

---

### PART 5 — Persistence (VM Reboot)

**Steps:**

1. While containers are running, add content in WordPress (a post or comment)
2. Shut down the VM completely
3. Reopen the VM
4. `cd ~/Inception && make`
5. Open the site — all content is still there

**Why it works:** Data lives on the host disk at `~/data/mysql` and `~/data/wordpress` (configured in `.env`). Containers are ephemeral, but the volumes point to the host filesystem.

---

### PART 6 — Making Changes (Ports, Config)


**Example 1 — Change HTTPS port (443 → 8443):**

Changing the external port requires edits in **2 files** plus a full data wipe, because WordPress stores the site URL (including the port) in its database and will redirect browsers to the old URL otherwise.

**Step 1.** In `srcs/docker-compose.yml`, change the host-side port mapping:
```yaml
ports:
  - "8443:443"    # was "443:443"
```
The format is `HOST_PORT:CONTAINER_PORT`. The left side (`8443`) is the port your browser connects to on the host. The right side (`443`) stays the same — NGINX inside the container still listens on 443, and Docker handles the translation. No need to touch `nginx.conf`.

**Step 2.** In `srcs/requirements/wordpress/tools/setup_wordpress.sh`, add the port to the install URL:
```bash
--url="https://${DOMAIN_NAME}:8443"    # was "https://${DOMAIN_NAME}"
```
WordPress saves this URL in its `wp_options` database table (`siteurl` and `home` rows). If the port is missing, WordPress will redirect every request to `https://slangero.42.fr` (without `:8443`), which has nothing listening — causing a connection error or redirect loop.

**Step 3.** Wipe data and rebuild from scratch:
```bash
make clean    # removes volumes + data directories (old DB with old URL is deleted)
make          # recreates everything, setup_wordpress.sh runs with the new URL
```
A simple `make re` is **not enough** — it rebuilds images but the database volume may survive with the old URL baked in.

**Step 4.** Clear your browser cache (`Ctrl+Shift+Delete` → Cookies + Cache → Clear), then visit `https://slangero.42.fr:8443`.

> **Why does `nginx.conf` stay unchanged?** Docker's port mapping handles the translation: the browser connects to host port 8443, Docker forwards it to container port 443, and NGINX (listening on 443) receives it normally. Only the host-side port changes.
>
> **Why is the data wipe mandatory?** WordPress stores `siteurl` and `home` in its database at install time. If these don't include `:8443`, WordPress will redirect every browser request to the portless URL. Wiping the data lets `setup_wordpress.sh` reinstall with the correct URL.
>
> **Alternative without data wipe:** If you want to keep existing content, skip step 2 and instead update the database directly after the containers are running:
> ```bash
> docker exec wordpress wp option update siteurl 'https://slangero.42.fr:8443' --allow-root --path=/var/www/html
> docker exec wordpress wp option update home 'https://slangero.42.fr:8443' --allow-root --path=/var/www/html
> ```


**Example 2 — Change PHP-FPM max children:**

In `srcs/requirements/wordpress/conf/www.conf`:
```ini
pm.max_children = 10   ; was 5
```
Then `make re` and verify: `docker exec wordpress cat /etc/php/7.4/fpm/pool.d/www.conf | grep max_children`

**Example 3 — Change MariaDB character set:**

In `srcs/requirements/mariadb/conf/50-server.cnf`:
```ini
character-set-server = utf8   ; was utf8mb4
```
Then `make re` and verify: `docker exec -it mariadb mysql -u root -p -e "SHOW VARIABLES LIKE 'character_set_server';"`

---

### PART 7 — Source Code Review


**"Each Docker image has the same name as its service"**

```bash
docker ps --format "table {{.Names}}\t{{.Image}}"
```

In `docker-compose.yml`, each service (`mariadb`, `wordpress`, `nginx`) has `container_name:` matching the service name.

**"Images are built yourself, not pulled from DockerHub"**

```bash
grep -r "^FROM" srcs/requirements/*/Dockerfile
```

Output: `FROM debian:bullseye` for all three. All services use `build:` in docker-compose.yml, not `image:`. Alpine/Debian base images are allowed per the subject.

**"Penultimate stable version of Alpine or Debian"**

`debian:bullseye` is Debian 11. At the time this project was created, Debian 12 (bookworm) was the latest stable release, making bullseye the penultimate stable version.

**"Dockerfiles called by docker-compose.yml by your Makefile"**

The chain is: `Makefile` -> `run_docker.sh` -> `docker compose -f srcs/docker-compose.yml up --build` -> each service's `Dockerfile`.

**"TLSv1.2 or TLSv1.3 only"**

```bash
grep ssl_protocols srcs/requirements/nginx/conf/nginx.conf
```

Output: `ssl_protocols TLSv1.2 TLSv1.3;`

**"WordPress + php-fpm without nginx"**

The WordPress Dockerfile only installs `php7.4-fpm`. PHP-FPM listens on port 9000 (internal). No nginx binary exists in this container:
```bash
docker exec wordpress which nginx   # fails
```

**"MariaDB without nginx"**

Same check:
```bash
docker exec mariadb which nginx   # fails
```

**"Docker named volumes"**

```bash
docker volume ls
docker volume inspect srcs_mariadb_data
docker volume inspect srcs_wordpress_data
```

Both volumes store data at `/home/slangero/data/` on the host machine.

**"Docker network"**

```bash
docker network ls
docker network inspect srcs_inception
```

Shows all three containers connected to the `inception` bridge network.

---

### PART 8 — Architecture Question

WordPress content does not come from the internet directly, it comes through your reverse proxy. 
The request flow is:

```
Browser --HTTPS:443--> nginx (reverse proxy)
                          |
                    FastCGI:9000
                          |
                          v
                      wordpress (php-fpm)
                          |
                     MySQL:3306
                          |
                          v
                       mariadb
```

- **nginx** is the only public entry point (only port exposed: 443)
- nginx receives the HTTPS request and proxies it internally to WordPress on port 9000 via FastCGI
- WordPress processes PHP and talks to MariaDB on port 3306
- Nothing reaches WordPress or MariaDB directly from the internet

Show in code:

```bash
grep fastcgi_pass srcs/requirements/nginx/conf/nginx.conf
# Output: fastcgi_pass wordpress:9000;
```

**"Are services nuilt separately or sequentially?"**

The services were designed with a dependency chain:

1. **MariaDB first** — standalone database, no dependencies
2. **WordPress second** — `depends_on: mariadb` — built knowing MariaDB exists, connects to it on startup
3. **nginx third** — `depends_on: wordpress` — built knowing WordPress serves PHP on port 9000

This is visible in `docker-compose.yml` via the `depends_on` directives, and in the startup scripts (`setup_wordpress.sh` waits for MariaDB to be ready before proceeding).

---

### Quick Reference — Commands to Have Ready

```bash
# Show all running containers
docker ps

# Show volumes and networks
docker volume ls
docker network ls

# Connect to MariaDB
docker exec -it mariadb mysql -u wpuser -p wordpress

# Check nginx TLS config
docker exec nginx nginx -T | grep ssl_protocols

# Verify no nginx in other containers
docker exec wordpress which nginx   # fails
docker exec mariadb which nginx     # fails

# Check Dockerfile base images
grep -r "^FROM" srcs/requirements/*/Dockerfile

# Inspect network
docker network inspect srcs_inception

# Full rebuild
cd ~/Inception && make re

# Container logs (useful for debugging)
docker logs nginx
docker logs wordpress
docker logs mariadb
```



