# Inception Project — Updated Plan

## Progress Review (as of latest commits)

### DONE
- [x] Step 2: Docker secrets wired into docker-compose.yml + entrypoint scripts
- [x] Step 5: Documentation written (README.md, USER_DOC.md, DEV_DOC.md)
- [x] Entrypoint scripts use `exec` for PID 1
- [x] Bounded retry loops (no `while true`)
- [x] `restart: unless-stopped` on all containers
- [x] No `network: host`, `--link`, `links:` in docker-compose
- [x] No `latest` tag in Dockerfiles
- [x] No passwords in Dockerfiles
- [x] Named volumes with host-path mapping
- [x] NGINX sole entry point on port 443, TLSv1.2/TLSv1.3
- [x] Admin username `superuser` (no "admin"), two WP users configured
- [x] README has italic first line, all required sections + 4 comparisons + AI usage

### CRITICAL ISSUES REMAINING

1. **`srcs/.env` is tracked in git** — Commit 03a2934 added it. `.gitignore` lists it but the file was committed before/force-added. Must `git rm --cached srcs/.env` to untrack. Evaluators WILL check `git ls-files` and this alone can fail the project.

2. **`secrets/` directory does not exist** — No folder, no files. Docker-compose WILL fail at startup because it references `../secrets/db_password.txt`, `../secrets/db_root_password.txt`, `../secrets/credentials.txt`. This is 100% blocking.

3. **`.dockerignore` files are all empty** — Should exclude `.git`, `*.md`, `tools/`, etc. from build context. Minor but shows lack of polish.

4. **`Makefile` `fclean` just aliases `clean`** — Should also remove Docker images (`docker rmi`) for a true full clean. Evaluators may test `make fclean && make re`.

5. **`run_docker.sh` sed runs before .env existence check** — Line 16 does `sed -i` on `.env`, line 18 checks if it exists. Swap order or guard the sed.

6. **`run_docker.sh` runs `docker compose up` in foreground** — No `-d` flag. Terminal stays locked. Evaluators expect to get their prompt back.

---

## PRIORITY LIST — What To Do Next

### P0 — DO THESE FIRST (project-failing if missed)

#### 1. Untrack `.env` from git
```bash
git rm --cached srcs/.env
git commit -m "Remove .env from git tracking (security requirement)"
```
Verify: `git ls-files srcs/.env` should return nothing.

#### 2. Create secrets directory and files
```bash
mkdir -p secrets
echo "CHANGE_ME" > secrets/db_password.txt
echo "CHANGE_ME" > secrets/db_root_password.txt
printf "WP_ADMIN_PASSWORD=CHANGE_ME\nWP_USER_PASSWORD=CHANGE_ME\n" > secrets/credentials.txt
```
These must exist locally but NOT be committed (already gitignored).

#### 3. First build test
- Ensure `/etc/hosts` has `127.0.0.1 slangero.42.fr`
- Run `make re`
- Debug until all 3 containers are running
- Verify `https://slangero.42.fr` loads WordPress

### P1 — FIX BEFORE EVALUATION

#### 4. Fix Makefile targets
```makefile
all:
	@bash run_docker.sh

clean:
	@bash run_docker.sh --clean

fclean: clean
	@docker rmi -f $$(docker images -qa) 2>/dev/null || true

re: fclean all

.PHONY: all clean fclean re
```

#### 5. Fix `run_docker.sh`
- Move the `.env` existence check BEFORE the sed command
- Add `-d` flag to `docker compose up` so it runs detached
- Consider adding a final health check / status message

#### 6. Populate `.dockerignore` files
Each service's `.dockerignore` should contain:
```
.git
*.md
.dockerignore
```

### P2 — TESTING & VERIFICATION

#### 7. Full clean test cycle
- `make fclean` then `make re` — from absolute scratch
- Verify WordPress loads, both users can log in
- `make clean` then `make` — verify data persists
- Check: `docker ps` shows 3 containers, all healthy
- Check: `docker volume ls` shows named volumes
- Check: `docker network ls` shows inception network

#### 8. Requirements checklist walkthrough
- [ ] `git ls-files srcs/.env` returns nothing
- [ ] `git ls-files secrets/` returns nothing
- [ ] No passwords anywhere in git history (consider `git log -p --all -S "password"`)
- [ ] Containers restart on crash: `docker kill wordpress && sleep 5 && docker ps`
- [ ] NGINX only entry: `docker port nginx` shows only 443
- [ ] TLS version: `openssl s_client -connect slangero.42.fr:443 -tls1_2`
- [ ] WordPress admin panel: `https://slangero.42.fr/wp-admin`
- [ ] Two users exist with correct roles

### P3 — BONUS (only if mandatory is perfect)

#### 9. Bonus services (optional)
- **Redis cache** — easiest, best value
- **Adminer** — quick win
- **Static website** — HTML/CSS/JS, no PHP
- Each needs: own Dockerfile, own container, entry in docker-compose

### P4 — DEFENSE PREP

#### 10. Know your project inside out
- Explain full request flow: Browser → NGINX (443/SSL) → PHP-FPM (9000) → WP → MariaDB (3306)
- Know Docker commands: `exec`, `logs`, `inspect`, `volume ls`, `network inspect`
- Be ready for live modifications during evaluation
- Understand WHY each design choice was made (secrets vs env, bridge vs host, volumes vs bind)
