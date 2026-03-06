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
cd inceptionz
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

`srcs/.env` contains non-sensitive configuration. It is also gitignored. An example is provided in `srcs/.env.example`. The `run_docker.sh` script automatically updates the data paths to match the current `$USER`.

## Building and Launching

### Using the Makefile

| Command | What it does |
|---------|-------------|
| `make` | `docker compose up --build` — incremental build + start |
| `make re` | Full clean + `docker compose build --no-cache` + start |
| `make clean` | `docker compose down --volumes` + remove data dirs + prune |

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
docker exec wordpress ping -c 2 mariadb
docker exec nginx ping -c 2 wordpress
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
inceptionz/
├── Makefile                           # Build targets (all, clean, re)
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
    ├── .env                           # Gitignored — non-sensitive config
    ├── .env.example                   # Template for .env
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
