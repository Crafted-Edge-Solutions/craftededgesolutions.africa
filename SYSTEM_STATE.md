# System State & Configuration Map

**Last Updated**: May 11, 2026  
**System**: WSL2 (Ubuntu 24.04 Noble) on Windows  
**User**: craftededgesolutions-africa  
**Hostname**: meshackvsyouall

---

## Service Status At A Glance

| Service | Status | Port | Access |
|---------|--------|------|--------|
| OpenWebUI (Docker) | ✅ Running | 3000 | localhost:3000 / 100.124.18.6:3000 |
| Ollama (systemd) | ✅ Running | 11434 | localhost:11434 (API) |
| Listmonk DB (Docker) | ✅ Running | 5432 (internal) | — |
| Listmonk App (Docker) | ❌ Crashed | 9000 | Needs restart |
| Website Server | ❌ Not running | 8000 | Start manually (see below) |
| Tailscale | ✅ Active | — | 100.124.18.6 |

---

## Network Access

### Tailscale
- **IP**: `100.124.18.6`
- **Account**: meshackmogire406@
- **Purpose**: Secure remote access from phone, laptop, anywhere

### SSH
- **Host**: `100.124.18.6` (Tailscale only)
- **User**: `craftededgesolutions-africa`
- **Auth**: SSH Key (see SSH_SETUP.md)

---

## Services Detail

### OpenWebUI (AI Chat Interface)
- **Status**: ✅ Healthy, auto-restarts on boot
- **URL**: http://localhost:3000 | http://100.124.18.6:3000
- **Container**: `open-webui` (Docker, `ghcr.io/open-webui/open-webui:main`)
- **Connected to**: Ollama at `http://host.docker.internal:11434`
- **Models available**: All Ollama models + can add OpenRouter
- **Manage**:
  ```bash
  docker restart open-webui
  docker logs open-webui --tail=30
  ```

### Ollama (Local AI Inference)
- **Status**: ✅ Running (systemd service, auto-starts)
- **API**: http://localhost:11434
- **Config**: `/etc/systemd/system/ollama.service`
- **Models stored**: `/usr/share/ollama/.ollama/models/` (~22 GB)
- **GPU**: NVIDIA GTX 960, 4GB VRAM — 3B models run at 22-32 tok/s on GPU
- **Custom modelfiles**: `~/.ollama/modelfiles/`
- **Manage**:
  ```bash
  sudo systemctl status ollama
  sudo systemctl restart ollama
  ollama list                     # show all models
  ollama ps                       # show loaded models
  ```

### Listmonk Email Platform
- **Status**: ❌ App crashed (exit 127) — DB is fine
- **Fix**: `docker start listmonk_app`
- **URL**: http://localhost:9000 | http://100.124.18.6:9000
- **Admin**: admin / password ⚠️ (change this)
- **SMTP**: Not configured — still shows placeholder `username@smtp.yoursite.com`
- **Compose file**: `~/craftededgesolutions.africa/docker-compose.listmonk.yml`
- **Manage**:
  ```bash
  docker start listmonk_app
  docker logs listmonk_app --tail=30
  cd ~/craftededgesolutions.africa && docker compose -f docker-compose.listmonk.yml up -d
  ```

### Website Server (craftededgesolutions.africa)
- **Status**: ❌ Not running (needs manual start after WSL restart)
- **Type**: Python HTTP server (static files)
- **Port**: 8000
- **Start**:
  ```bash
  cd ~/craftededgesolutions.africa && python3 -m http.server 8000 &
  ```
- **URL**: http://localhost:8000 | http://100.124.18.6:8000

---

## AI Stack

### Models (Ollama local)

**GPU-accelerated (22-32 tok/s) — use for interactive work:**

| Alias | Model | VRAM | Use |
|-------|-------|------|-----|
| `qwen` | qwen-fast (qwen2.5:3b Q4_K_M) | ~2.0GB | General chat |
| `coder` | qwen-coder-fast (qwen2.5-coder:3b) | ~2.0GB | Code |
| `think` | r1-fast (deepseek-r1:1.5b) | ~1.3GB | Reasoning |
| `phi` | phi3-fast (phi3:mini) | ~2.4GB | Instructions |
| `gemma` | gemma3:4b | ~3.5GB | Best local quality |

**CPU-only (0.7 tok/s) — batch jobs only, GTX 960 Maxwell CUDA incompatible:**

| Alias | Model | Use |
|-------|-------|-----|
| `qwen7` | qwen2.5:7b | High quality general |
| `coder7` | qwen2.5-coder:7b | High quality code |

**Embeddings:** `nomic-embed-text` — for RAG/document search

### Cloud (OpenRouter free tier)
| Alias | Model | Use |
|-------|-------|-----|
| `hgemma` | Gemma 4 31B | Best quality (default) |
| `hllama` | Llama 3.3 70B | Research/reasoning |
| `hgpt` | GPT-OSS 20B | OpenAI-style tasks |

### Agents
- **Hermes** (`h`, `hask`): Full agent — Spotify, web search, files, cron, delegation. Config: `~/.hermes/config.yaml`. Default: Gemma4-31B cloud, fallback: gemma3:4b local.
- **Pi** (`p`, `pask`): Coding agent — reads/edits/runs files. Config: `~/.pi/agent/settings.json`. Default: Gemma4-31B cloud.

### Key AI Files
| File | Purpose |
|------|---------|
| `~/.hermes/config.yaml` | Hermes model, provider, cron, personalities |
| `~/.hermes/auth.json` | Spotify + API tokens |
| `~/.pi/agent/settings.json` | Pi default model/provider |
| `~/.bash_aliases` | All AI terminal aliases |
| `~/.ollama/modelfiles/` | Custom model Modelfiles |
| `~/.ollama/register-fast-models.sh` | Re-register all custom variants |
| `~/ai-stack-guide.md` | Full AI stack guide with use cases |

---

## Project Structure

```
/home/craftededgesolutions-africa/
├── craftededgesolutions.africa/        ← Main Crafted Edge project
│   ├── SYSTEM_STATE.md                 ← This file
│   ├── QUICK_REFERENCE.md              ← One-page command ref
│   ├── docker-compose.listmonk.yml     ← Listmonk email platform
│   ├── listmonk/config.toml            ← Listmonk settings (SMTP here)
│   ├── *.html, style.css               ← Static website
│   └── .git/                           ← Git repo
├── wellness-solutions.africa/          ← WSA project
│   ├── docker-compose.yml
│   └── *.tsv                           ← Business data sheets
├── wsa-assets/, wsa-roaming-assets/    ← WSA media
├── ai-stack-guide.md                   ← Full AI guide (generated May 2026)
├── eisvogel/                           ← PDF template
└── .hermes/, .pi/, .ollama/            ← AI agent configs
```

---

## Docker Containers

| Container | Image | Status | Restart Policy |
|-----------|-------|--------|----------------|
| open-webui | open-webui:main | ✅ healthy | always |
| listmonk_db | postgres:14-alpine | ✅ healthy | always |
| listmonk_app | listmonk:latest | ❌ crashed | no (set to always!) |
| listmonk_app_init | listmonk:latest | exited 0 (normal) | no |
| welcome-to-docker | docker/welcome-to-docker | exited | no |

**Fix listmonk restart policy:**
```bash
docker update --restart=always listmonk_app
```

---

## Configuration Files Reference

| File | Path | Notes |
|------|------|-------|
| Ollama service | `/etc/systemd/system/ollama.service` | OLLAMA_FLASH_ATTENTION=0 set |
| Listmonk config | `~/craftededgesolutions.africa/listmonk/config.toml` | SMTP placeholder, needs real config |
| Listmonk compose | `~/craftededgesolutions.africa/docker-compose.listmonk.yml` | |
| Hermes config | `~/.hermes/config.yaml` | OpenRouter primary, Ollama fallback |
| Bash aliases | `~/.bash_aliases` | All shortcuts |
| Bashrc | `~/.bashrc` | OPENROUTER_API_KEY export |

---

## Credentials

| Service | Where stored | Notes |
|---------|-------------|-------|
| Listmonk admin | listmonk/config.toml | admin/password — change it |
| OpenRouter API key | `~/.bashrc` (OPENROUTER_API_KEY) | Free tier |
| Spotify token | `~/.hermes/auth.json` | Refresh with `spotify-refresh` |
| Tailscale | System | meshackmogire406@ |

Note: Keep sudo credentials out of documents — use a password manager.

---

## Quick Commands

```bash
# --- AI ---
h "your question"              # Hermes AI agent
hask "question"                # Hermes one-shot (no stdin loop)
qwen                           # Fast local chat (GPU)
gemma                          # Best local chat
play "song name"               # Play Spotify via Hermes

# --- Services ---
docker start listmonk_app      # Fix crashed listmonk
docker ps                      # Check all containers
cd ~/craftededgesolutions.africa && python3 -m http.server 8000 &   # Start website

# --- Monitoring ---
gpu                            # GPU stats
gpuwatch                       # Live GPU monitor
models                         # List AI models
ollama ps                      # Currently loaded models
docker stats                   # Container resource usage

# --- Tailscale ---
sudo tailscale status
sudo tailscale up

# --- Git (Crafted Edge site) ---
cd ~/craftededgesolutions.africa
git status
git log --oneline -5
```

---

## Known Issues & Fixes

| Issue | Status | Fix |
|-------|--------|-----|
| Listmonk app crashed | ❌ Active | `docker start listmonk_app` |
| Listmonk SMTP not configured | ❌ Active | Edit listmonk/config.toml smtp section |
| Listmonk restart policy not set | ❌ Active | `docker update --restart=always listmonk_app` |
| Website server not persistent | ⚠️ Cosmetic | Start manually after each WSL boot |
| 7B models crash on GPU | ⚠️ Known limit | GTX 960 Maxwell incompatible — use CPU or cloud |
| Listmonk admin password default | ⚠️ Security | Change at http://localhost:9000/settings/users |

---

## Startup Checklist (after WSL restart)

```bash
# 1. Verify Docker is up
docker ps

# 2. Start listmonk if down
docker start listmonk_app

# 3. Start website server
cd ~/craftededgesolutions.africa && python3 -m http.server 8000 &

# 4. Verify Ollama
curl http://localhost:11434/api/version

# 5. Verify OpenWebUI
curl -s http://localhost:3000 | head -3

# 6. Check Tailscale
sudo tailscale status
```

---

## Improvements To Do

### High Priority
- [ ] Configure Listmonk SMTP (Zoho/Gmail) — currently non-functional
- [ ] Change Listmonk admin password from default
- [ ] Set listmonk_app restart policy: `docker update --restart=always listmonk_app`
- [ ] Add OpenRouter to OpenWebUI: Settings → Connections → `https://openrouter.ai/api/v1` + API key

### Medium Priority  
- [ ] Add OLLAMA_HOST=0.0.0.0 to ollama.service (expose to LAN/Tailscale for mobile access)
- [ ] Set up website server as a systemd service (auto-start on boot)
- [ ] SQLite knowledge base for AI agents (`~/.knowledge/kb.db`)
- [ ] Blog writer cron job in Hermes (see `~/ai-stack-guide.md` section 6)

### Low Priority
- [ ] Pull deepseek-r1:7b (CPU-only on this GPU, but highest local reasoning quality)
- [ ] Set up automatic Listmonk DB backups
- [ ] GitHub Actions deployment workflow for craftededgesolutions.africa
- [ ] Add `nomic-embed-text` as embedding model in OpenWebUI for document RAG

---

*Update this file whenever configuration changes.*
