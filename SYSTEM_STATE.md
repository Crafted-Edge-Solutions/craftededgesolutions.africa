# System State & Configuration Map

**Last Updated**: May 9, 2026  
**System**: WSL2 (Ubuntu 24.04 Noble) on Windows  
**User**: craftededgesolutions-africa  
**Hostname**: meshackvsyouall

---

## 🌐 Network Access

### Tailscale
- **Status**: ✅ Active & Authenticated
- **Tailscale IP**: `100.124.18.6`
- **Account**: meshackmogire406@
- **Purpose**: Secure remote access, accessible from any device in the Tailscale network

### SSH Access
- **Host**: `100.124.18.6` (via Tailscale)
- **User**: `craftededgesolutions-africa`
- **Port**: 22 (default)
- **Auth**: SSH Key (see SSH_SETUP.md)
- **Password Access**: `sudo password: 7996` (use with caution)

---

## 📦 Running Services

### 1. **Website Server** (HTTP)
- **Status**: ✅ Running
- **Type**: Python HTTP Server
- **Port**: `8000`
- **Path**: `/home/craftededgesolutions-africa/craftededgesolutions.africa/`
- **Access**:
  - Local: `http://localhost:8000`
  - Tailscale: `http://100.124.18.6:8000`
  - Remote: `http://meshackvsyouall:8000` (if on same Tailscale network)
- **Process**: `python3 -m http.server 8000`
- **PID File**: `/tmp/http-server.pid`

### 2. **Listmonk Email Platform** (Docker)
- **Status**: ✅ Running (unhealthy flag - needs investigation)
- **Type**: Docker Compose Multi-container
- **Port**: `9000`
- **Access**:
  - Local: `http://localhost:9000`
  - Tailscale: `http://100.124.18.6:9000`
- **Admin Credentials**:
  - Username: `admin`
  - Password: `password` ⚠️ (change on first login)
- **Compose File**: `/home/craftededgesolutions-africa/craftededgesolutions.africa/docker-compose.listmonk.yml`
- **Database**: PostgreSQL 14 (listmonk_db container)
- **Volume**: `listmonk_data` (persistent storage)

### 3. **Docker Desktop Welcome** 
- **Status**: ✅ Running
- **Port**: `8088`
- **Purpose**: Default Docker welcome page (can be disabled)

---

## 💾 Project Structure

```
/home/craftededgesolutions-africa/
├── craftededgesolutions.africa/          (Main Project)
│   ├── docker-compose.listmonk.yml       (Email service config)
│   ├── listmonk/
│   │   └── config.toml                   (Listmonk config)
│   ├── index.html                        (Homepage)
│   ├── services.html                     (Services page)
│   ├── solutions.html                    (Solutions page)
│   ├── about.html                        (About page)
│   ├── contact.html                      (Contact page)
│   ├── builder.html                      (Builder teaser)
│   ├── editor.html                       (GrapesJS editor)
│   ├── style.css                         (Global styles)
│   ├── tweaks-panel.jsx                  (React component)
│   ├── robots.txt, sitemap.xml, llms.txt
│   ├── .git/                             (Git repository)
│   ├── .github/                          (GitHub workflows)
│   └── uploads/                          (GrapesJS backups)
├── wellness-solutions.africa/            (Sister project)
├── wsa-roaming-assets/                   (Assets)
└── wsa-assets/                           (More assets)
```

---

## 🔧 Configuration Files

| File | Path | Purpose |
|------|------|---------|
| Docker Compose | `/home/craftededgesolutions-africa/craftededgesolutions.africa/docker-compose.listmonk.yml` | Email service orchestration |
| Listmonk Config | `/home/craftededgesolutions-africa/craftededgesolutions.africa/listmonk/config.toml` | Listmonk settings |
| Website Files | `/home/craftededgesolutions-africa/craftededgesolutions.africa/*.html` | Static HTML pages |
| CSS | `/home/craftededgesolutions-africa/craftededgesolutions.africa/style.css` | Main stylesheet |

---

## 🐳 Docker Info

**Daemon Status**: ✅ Running (via Docker Desktop)  
**Docker Version**: 29.4.2  
**Networks**: `craftededgesolutionsafrica_default`  
**Volumes**: `craftededgesolutionsafrica_listmonk_data`

### Containers
```
listmonk_app     - Main email app (unhealthy - DB connection issue?)
listmonk_db      - PostgreSQL 14 database (healthy)
welcome-to-docker - Docker demo container
```

---

## 🔐 Credentials & Secrets

| Service | Username | Password | Notes |
|---------|----------|----------|-------|
| Listmonk Admin | `admin` | `password` | ⚠️ CHANGE IMMEDIATELY |
| PostgreSQL | `listmonk` | `listmonk` | Docker env var, internal only |
| Sudo/Root | N/A | `7996` | WSL sudo password |
| Tailscale | meshackmogire406@ | (OAuth) | Connected |

---

## 📝 Recent Work (Git Log)

```
960bcf9 feat: add Managed Email Marketing service and Listmonk infrastructure
b0afa5a style: switch heading font from Syne to Montserrat Bold
986ad78 fix: correct builder teaser rendering and style consistency
f40bbf6 feat: add Crafted Builder teaser page, SEO FAQ schema, and nav updates
bac8d2e seo: add structured data, Open Graph, Twitter Cards, favicon, and keyword meta
```

---

## 🔄 Startup Checklist

- [ ] Docker Desktop running (required for containers)
- [ ] Tailscale authenticated (`tailscale status`)
- [ ] Website server running (`ps aux | grep http.server`)
- [ ] Listmonk containers up (`docker-compose ps`)
- [ ] Ports accessible (`curl http://100.124.18.6:8000` & `:9000`)

---

## 🚀 Quick Commands

```bash
# Check all services
echo "7996" | sudo -S docker-compose -f craftededgesolutions.africa/docker-compose.listmonk.yml ps

# Restart Listmonk
echo "7996" | sudo -S docker-compose -f craftededgesolutions.africa/docker-compose.listmonk.yml restart

# View Listmonk logs
echo "7996" | sudo -S docker-compose -f craftededgesolutions.africa/docker-compose.listmonk.yml logs app

# Check Tailscale
echo "7996" | sudo -S tailscale status

# Restart website server
pkill -f "http.server 8000"
cd craftededgesolutions.africa && python3 -m http.server 8000 &
```

---

## ⚠️ Known Issues

1. **Listmonk Unhealthy Status**: Database connection may be flaky
   - Fix: Restart containers with `docker-compose restart`
   
2. **Sudo Password Required**: Most privileged commands need password
   - Workaround: Use `echo "7996" | sudo -S` prefix

3. **Docker Daemon Permissions**: User not in docker group
   - Workaround: Use `sudo` or add user to group

---

## 📌 To Remember

- **Base Path**: `/home/craftededgesolutions-africa/`
- **Tailscale IP**: `100.124.18.6` (share this for remote access)
- **Sudo Password**: `7996` (keep secure)
- **Project Ports**: 8000 (website), 9000 (email), 8088 (docker)
- **Docker Daemon**: Start via Docker Desktop on Windows
- **SSH Ready**: Use Tailscale IP for secure remote access

---

## Next Steps

- [ ] Change Listmonk admin password
- [ ] Integrate Zoho SMTP into Listmonk
- [ ] Set up automatic backups for Listmonk database
- [ ] Configure GitHub workflows for deployment
- [ ] Set up monitoring/health checks

---

*This is a living document. Update whenever system configuration changes.*
