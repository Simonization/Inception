# Inception Project — Updated Plan (March 6, 2026)

## Status: MANDATORY PART COMPLETE — Ready for evaluation

---

## COMPLETED

### P0 — Critical (all fixed)
- [x] `.env` untracked from git (`git ls-files srcs/.env` returns nothing)
- [x] `secrets/` directory created with password files (not committed)
- [x] Docker secrets wired into docker-compose.yml + entrypoint scripts
- [x] First build test passed — all 3 containers running, WordPress loads

### P1 — Pre-evaluation fixes (all done)
- [x] Makefile `fclean` removes images + system prune
- [x] `run_docker.sh` — `.env` check before sed, `-d` flag for detached mode
- [x] `.dockerignore` files populated (`.git`, `*.md`, `.dockerignore`)
- [x] WordPress setup race condition fixed (`--skip-check` + `wp db check` retry loop)

### P2 — Testing & verification (all passed)
- [x] **Data persistence**: comment survived `docker compose down && up`
- [x] **Auto-restart**: `docker exec wordpress kill 1` → container restarts automatically (confirmed by uptime reset)
- [x] **Ports**: `docker port nginx` shows only `443/tcp` (IPv4 + IPv6)
- [x] **TLS 1.2**: `openssl s_client -tls1_2` → Protocol: TLSv1.2, Cipher: ECDHE-RSA-AES256-GCM-SHA384
- [x] **TLS 1.3**: `openssl s_client -tls1_3` → Protocol: TLSv1.3, Cipher: TLS_AES_256_GCM_SHA384
- [x] **Git tracking**: `git ls-files srcs/.env` and `git ls-files secrets/` return nothing
- [x] **WordPress admin**: both users can log in at `https://slangero.42.fr/wp-admin`
- [x] **Volumes**: `docker volume ls` shows `srcs_mariadb_data` and `srcs_wordpress_data`
- [x] **Network**: `docker network ls` shows `srcs_inception` with bridge driver
- [x] **3 containers**: mariadb, wordpress, nginx all running

### Architecture (already correct)
- [x] Entrypoint scripts use `exec` for PID 1
- [x] Bounded retry loops (no `while true`)
- [x] `restart: unless-stopped` on all containers
- [x] No `network: host`, `--link`, `links:` in docker-compose
- [x] No `latest` tag in Dockerfiles
- [x] No passwords in Dockerfiles
- [x] Named volumes with host-path binding
- [x] NGINX sole entry point on port 443
- [x] Admin username `superuser` (no "admin"), two WP users with different roles
- [x] README has italic first line, all required sections + 4 comparisons + AI usage

---

## EVALUATION CHEAT SHEET

### Quick demo commands
```bash
# Show containers
docker ps

# Show volumes and network
docker volume ls
docker network ls

# Show only port 443 exposed
docker port nginx

# TLS verification
echo | openssl s_client -connect slangero.42.fr:443 -tls1_2 2>&1 | grep "Protocol\|Cipher"
echo | openssl s_client -connect slangero.42.fr:443 -tls1_3 2>&1 | grep "Protocol\|Cipher"

# Auto-restart proof
docker exec wordpress kill 1 && sleep 15 && docker ps

# Git security check
git ls-files srcs/.env
git ls-files secrets/
```

### Key explanations for corrector
- **Request flow**: Browser → NGINX (443/TLS) → PHP-FPM (9000/TCP) → WordPress → MariaDB (3306)
- **Why two users?** Principle of least privilege — superuser (admin) manages the site, slangero (author) writes content only
- **Why `docker exec kill 1` not `docker kill`?** Simulates a real process crash; `docker kill` sends SIGKILL to container runtime which can bypass restart handler in some Docker versions
- **Why Docker secrets?** Passwords mounted as files at runtime (`/run/secrets/`), never baked into images or environment variables
- **Why bridge network?** Containers communicate by service name (DNS), isolated from host network
- **Why named volumes with bind mount?** Data persists across container rebuilds, stored at a known host path

---

## P3 — BONUS (only if mandatory is perfect)

#### Bonus services (optional)
- **Redis cache** — easiest, best value
- **Adminer** — quick win
- **Static website** — HTML/CSS/JS, no PHP
- Each needs: own Dockerfile, own container, entry in docker-compose
