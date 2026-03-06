# User Documentation — Inception

## Services Overview

This stack provides a complete WordPress website served over HTTPS. It consists of three services:

- **NGINX** — Web server and reverse proxy. Handles HTTPS connections on port 443, serves static files, and forwards PHP requests to WordPress.
- **WordPress + PHP-FPM** — The content management system that generates web pages. It processes PHP code and communicates with the database.
- **MariaDB** — Relational database that stores all WordPress content: posts, pages, user accounts, settings, and more.

## Starting and Stopping the Project

### Start the project

```bash
make
```

This builds any changed images and starts all containers. If the stack was previously running, it picks up where it left off with existing data.

### Start from scratch (clean rebuild)

```bash
make re
```

This removes all containers, volumes, and data directories, rebuilds every image without cache, and starts fresh. Use this for a first-time setup or to reset everything.

### Stop and clean up

```bash
make clean
```

This stops all containers and removes volumes and data. The project will not be running after this command.

## Accessing the Website

Once the stack is running, open your browser and navigate to:

```
https://slangero.42.fr
```

Your browser will show a security warning because the SSL certificate is self-signed. This is expected — click "Advanced" and "Accept the risk" (or equivalent) to proceed.

### WordPress Admin Panel

Access the administration dashboard at:

```
https://slangero.42.fr/wp-admin
```

Log in with the administrator credentials (see "Managing Credentials" below).

From the admin panel you can create posts, manage users, install themes, and configure site settings.

### Secondary User

A secondary user account with the "Author" role is also created during setup. Authors can write and publish their own posts but cannot modify site settings or manage other users.

## Managing Credentials

All passwords are stored in the `secrets/` directory at the root of the repository. This directory is gitignored and never pushed to version control.

| File | Contains | Used by |
|------|----------|---------|
| `secrets/db_password.txt` | Database user password | MariaDB, WordPress |
| `secrets/db_root_password.txt` | Database root password | MariaDB |
| `secrets/credentials.txt` | WordPress admin and user passwords | WordPress |

Non-sensitive configuration (usernames, domain name, email addresses, paths) is stored in `srcs/.env`, which is also gitignored.

### Changing passwords

1. Edit the relevant file in `secrets/`
2. Run `make re` to rebuild and restart with the new passwords

Note: changing database passwords requires a fresh start (`make re`) since the existing database was initialized with the old passwords.

## Checking That Services Are Running

### Quick check — all containers

```bash
docker ps
```

You should see three containers running: `nginx`, `wordpress`, and `mariadb`.

### Check individual service logs

```bash
docker logs nginx
docker logs wordpress
docker logs mariadb
```

### Test HTTPS connectivity

```bash
curl -k https://slangero.42.fr
```

The `-k` flag accepts the self-signed certificate. You should see HTML output from WordPress.

### Test database connectivity

```bash
docker exec mariadb mysqladmin ping -h localhost -u root -p"$(cat secrets/db_root_password.txt)"
```

Should respond with "mysqld is alive".

### Test PHP-FPM

```bash
docker exec wordpress php-fpm7.4 -t
```

Should respond with "test is successful".
