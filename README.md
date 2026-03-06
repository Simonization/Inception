*This project has been created as part of the 42 curriculum by slangero.*

# Inception

## Description

Inception is a system administration project that uses Docker to build a small web infrastructure from scratch. The goal is to set up three interconnected services — NGINX, WordPress with PHP-FPM, and MariaDB — each running in its own custom-built Docker container, orchestrated with Docker Compose.

The infrastructure serves a WordPress website over HTTPS (port 443) using a self-signed TLS certificate. All container images are built from Debian Bullseye using custom Dockerfiles — no pre-built images from Docker Hub are used (except the base OS). Data persists across restarts through Docker named volumes mapped to the host filesystem.

### Architecture Overview

```
Browser (HTTPS :443)
    │
    ▼
┌─────────┐     ┌───────────────┐     ┌──────────┐
│  NGINX  │────▶│ WordPress     │────▶│ MariaDB  │
│  :443   │     │ PHP-FPM :9000 │     │  :3306   │
└─────────┘     └───────────────┘     └──────────┘
    SSL/TLS         FastCGI              MySQL
```

All containers communicate through an isolated Docker bridge network called `inception`. NGINX is the sole entry point, accepting traffic only on port 443 with TLSv1.2/TLSv1.3.

## Instructions

### Prerequisites

- Docker and Docker Compose installed
- Access to modify `/etc/hosts` (or have `slangero.42.fr` already mapped to `127.0.0.1`)

### Quick Start

```bash
# Clone the repository
git clone <repo-url> && cd inceptionz

# Ensure /etc/hosts has the domain entry
# (may require admin privileges)
echo "127.0.0.1 slangero.42.fr" | sudo tee -a /etc/hosts

# Populate secrets/ with your passwords (files are gitignored)
echo "YourDbPassword" > secrets/db_password.txt
echo "YourRootPassword" > secrets/db_root_password.txt
printf "WP_ADMIN_PASSWORD=YourAdminPass\nWP_USER_PASSWORD=YourUserPass\n" > secrets/credentials.txt

# Build and launch
make re

# Access the site
# https://slangero.42.fr (accept the self-signed certificate warning)
```

### Makefile Targets

| Command | Action |
|---------|--------|
| `make` | Start with existing data (rebuild if changed) |
| `make re` | Clean everything and rebuild from scratch |
| `make clean` | Stop all services and remove volumes/data |

## Project Description

### Why Docker?

Docker allows packaging applications with all their dependencies into lightweight, portable containers. Unlike installing services directly on the host OS — where dependency conflicts, version mismatches, and OS differences cause constant issues — Docker guarantees that if it works in one environment, it works everywhere.

For this project, Docker lets us run NGINX, WordPress, and MariaDB in isolated environments that communicate over a private network, each with their own filesystem, dependencies, and configuration.

### Virtual Machines vs Docker

Virtual machines emulate an entire computer with its own OS kernel, hardware abstraction layer, and full operating system. Each VM typically requires gigabytes of disk space and significant RAM overhead. They boot in minutes and provide strong isolation through hardware-level virtualization.

Docker containers share the host's kernel and only package the application layer — libraries, binaries, and config files. They start in seconds, use megabytes instead of gigabytes, and provide process-level isolation through Linux namespaces and cgroups. The tradeoff is weaker isolation compared to VMs, since all containers share the same kernel.

For this project, Docker is the better choice: we need lightweight, fast-starting services that communicate over a network, not full OS emulation.

### Secrets vs Environment Variables

Environment variables (stored in `.env`) are the standard way to configure containers. They're simple, readable, and supported everywhere. However, they appear in `docker inspect` output, process listings, and logs — making them unsuitable for passwords and API keys.

Docker secrets are files mounted into containers at `/run/secrets/`, readable only by the container's processes, stored encrypted at rest, and never exposed in inspect output or logs. They're the recommended approach for any sensitive data.

This project uses both: `.env` for non-sensitive configuration (domain name, database name, usernames, paths) and Docker secrets for all passwords.

### Docker Network vs Host Network

Host networking (`network: host`) removes all network isolation — the container shares the host's network stack directly. This is simpler but defeats one of Docker's key security features: containers can see and access all host ports and services.

Bridge networking (used in this project) creates an isolated virtual network. Containers communicate with each other using service names as hostnames (e.g., `wordpress` can reach `mariadb:3306`), but are invisible to the host unless ports are explicitly published. Only NGINX exposes port 443 to the host — MariaDB and WordPress are completely internal.

### Docker Volumes vs Bind Mounts

Bind mounts map a specific host directory into a container. They're simple but tightly couple the container to the host's filesystem layout and can cause permission issues.

Docker named volumes are managed by Docker itself. They provide better portability, can be backed up and migrated with Docker commands, and work consistently across different host systems. This project uses named volumes with a `local` driver configured to store data under `/home/slangero/data/`, combining the benefits of named volumes (Docker-managed lifecycle) with a predictable host storage location.

## Resources

### Documentation and References

- [Docker official documentation](https://docs.docker.com/)
- [Docker Compose reference](https://docs.docker.com/compose/compose-file/)
- [NGINX configuration guide](https://nginx.org/en/docs/)
- [WordPress CLI (WP-CLI) handbook](https://make.wordpress.org/cli/handbook/)
- [MariaDB knowledge base](https://mariadb.com/kb/en/)
- [Docker secrets documentation](https://docs.docker.com/compose/how-tos/use-secrets/)
- [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/)
- Thanks to Eduardo for guidance

### Videos

- [full course on Docker, recommended on Slack World, 4h](https://www.youtube.com/watch?v=RqTEHSBrYFw)
- [docker in 18min](https://www.youtube.com/watch?v=Ud7Npgi6x8E)
- [Docker in 5min, bande de codeurs](https://www.youtube.com/watch?v=mspEJzb8LC4)
- [Docker file & docker compose, bande de codeurs, 17min](https://www.youtube.com/watch?v=ES4BcZcsBdU)
- [Docker in 100 Seconds, Fireship](https://youtu.be/Gjnup-PuquQ)
- [100 Docker Concepts you Need to know, Fireship, 8min](https://youtu.be/rIrNIzy6U_g?si=V6OE1NSWnh8RSdOF)
- [Kubernetes in 100 Seconds, Fireship](https://youtu.be/PziYflu8cB8)
  
### AI Usage

AI (Claude by Anthropic) was used as a development assistant throughout this project for:

- **Planning**: Creating a structured work plan
- **Code review**: Analyzing existing Dockerfiles, entrypoint scripts, and docker-compose configuration for issues and improvements
- **Documentation**: Drafting README.md, USER_DOC.md, and DEV_DOC.md based on project requirements
- **Debugging**: Troubleshooting container communication issues, volume permissions, and MariaDB initialization

All AI-generated code and documentation was reviewed, understood, and adapted by the student before inclusion in the project.

