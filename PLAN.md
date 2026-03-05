# Inception Project — 2-Day Plan

## Current State

The repo has all core infrastructure files in place:
- 3 Dockerfiles (nginx, mariadb, wordpress) — all debian:bullseye
- 3 config files (nginx.conf, 50-server.cnf, www.conf)
- 3 entrypoint scripts (setup_ssl.sh, setup_mariadb.sh, setup_wordpress.sh)
- docker-compose.yml with volumes, networks, depends_on
- .env / .env.example / .gitignore
- Makefile + run_docker.sh

## Issues to Fix Before Testing

1. **`/etc/hosts`** — Need `127.0.0.1 slangero.42.fr` added (requires admin or pre-existing entry)
2. **Docker secrets** — Passwords are only in `.env`. The subject says credentials in the repo (outside secrets) = failure. Must wire `secrets/` files into docker-compose and entrypoint scripts.
3. **Documentation** — README.md, USER_DOC.md, DEV_DOC.md are all empty and mandatory for validation.
4. **`.dockerignore` files** — All empty, should exclude unnecessary files from build context.

---

## DAY 1 — Thursday (8:00–20:00, ~12h)

### Step 1: Fix sudo & first build (1.5h)
- Confirm `run_docker.sh` has no sudo commands
- Check `/etc/hosts` for domain entry, get it added if missing
- Run `make re` — get the first build attempt going
- Debug any immediate build failures

### Step 2: Add Docker secrets (2h)
- Populate `secrets/db_password.txt`, `secrets/db_root_password.txt`, `secrets/credentials.txt`
- Add `secrets:` section to `docker-compose.yml`
- Update entrypoint scripts to read from `/run/secrets/` files
- Keep `.env` for non-sensitive config (DOMAIN_NAME, SQL_DATABASE, data paths)

### Step 3: Test & debug full stack (3h)
- MariaDB starts and initializes the database
- WordPress connects to MariaDB and completes installation
- NGINX serves WordPress over HTTPS on port 443
- `https://slangero.42.fr` loads in browser (accept self-signed cert warning)
- Both WP users exist: admin ("superuser") + author
- Verify admin username doesn't contain "admin" (superuser is fine)

### Step 4: Verify all project requirements (1.5h)
Checklist:
- [ ] Containers restart on crash (`restart: unless-stopped`)
- [ ] No `tail -f`, `sleep infinity`, `while true` in scripts
- [ ] No `network: host`, `--link`, or `links:` in docker-compose
- [ ] No `latest` tag in Dockerfiles
- [ ] No passwords in Dockerfiles
- [ ] Named volumes (not raw bind mounts)
- [ ] NGINX is sole entry point on port 443 only
- [ ] TLSv1.2 or TLSv1.3 only
- [ ] All scripts use `exec` for PID 1 best practice
- [ ] `.env` is gitignored
- [ ] Secrets folder is gitignored

### Step 5: Write documentation (2h)
- **README.md**: project description, instructions, resources, AI usage, comparisons (VM vs Docker, Secrets vs Env, Docker Network vs Host, Volumes vs Bind Mounts)
- **USER_DOC.md**: services overview, start/stop, access website + admin panel, manage credentials, verify services
- **DEV_DOC.md**: prerequisites, setup from scratch, build & launch with Makefile, container/volume management, data storage & persistence

### Buffer/Breaks: ~2h

---

## DAY 2 — Friday (11:00–19:00, ~8h)

### Step 6: Full clean test (1.5h)
- `make fclean` then `make re` — test from absolute scratch
- Verify data persists: `make clean` then `make` (should keep data)
- Confirm WordPress loads, both users work, HTTPS works

### Step 7: Bonus services (3h, optional — only if mandatory is perfect)
- **Redis cache** for WordPress (easiest bonus)
- **Adminer** (quick database UI, one Dockerfile)
- **Static website** (simple HTML/CSS/JS, not PHP)
- Each bonus = own Dockerfile + own container + entry in docker-compose

### Step 8: Defense preparation (2h)
- Practice explaining: Docker architecture, container communication, full request flow
- Know commands: `docker exec`, `docker logs`, `docker inspect`, `docker volume ls`
- Be ready for live code modifications during evaluation
- Understand: browser → NGINX (443/SSL) → PHP-FPM (9000) → WordPress → MariaDB (3306)

### Buffer: ~1.5h

---

## DAY 3 — Saturday: Corrections at school

---

## Time Summary

| Step | Description | Hours | When |
|------|------------|-------|------|
| 1 | Fix sudo + first build | 1.5 | Day 1 morning |
| 2 | Docker secrets | 2.0 | Day 1 morning |
| 3 | Test & debug full stack | 3.0 | Day 1 afternoon |
| 4 | Verify requirements | 1.5 | Day 1 late afternoon |
| 5 | Write 3 doc files | 2.0 | Day 1 evening |
| 6 | Full clean test | 1.5 | Day 2 morning |
| 7 | Bonus services (optional) | 3.0 | Day 2 afternoon |
| 8 | Defense prep | 2.0 | Day 2 evening |

**Total productive time: ~16.5h across 2 days**
