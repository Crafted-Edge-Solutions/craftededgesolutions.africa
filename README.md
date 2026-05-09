# Crafted Edge Solutions - Development Environment

**Status**: ✅ Live & Accessible  
**Last Updated**: May 9, 2026  
**Access**: Tailscale IP `100.124.18.6`

---

## 📖 Start Here

### 🚀 Quick Start (5 minutes)

1. **Access the website:**
   ```
   http://100.124.18.6:8000
   ```

2. **Access Listmonk (email):**
   ```
   http://100.124.18.6:9000
   Username: admin | Password: password
   ```

3. **SSH into the server:**
   ```bash
   ssh craftededgesolutions-africa@100.124.18.6
   # Password: 7996
   ```

---

## 📚 Documentation (READ IN ORDER)

### 1. **QUICK_REFERENCE.md** ⭐ (Start here!)
   - Quick access to common commands
   - Control everything (start/stop services)
   - Checklists and pro tips

### 2. **SYSTEM_STATE.md** (The source of truth)
   - Complete system configuration
   - All running services
   - Project structure
   - Known issues & fixes
   - Update this when config changes

### 3. **SSH_SETUP.md** (For remote access)
   - SSH access guide (multiple methods)
   - Key-based authentication setup
   - Troubleshooting
   - Platform-specific instructions

---

## 🏗️ System Architecture

```
Your Windows PC (Docker Desktop)
    ↓
WSL2 Ubuntu (meshackvsyouall)
    ├─ Website Server (Port 8000)
    │  └─ Python HTTP Server
    │     └─ Static HTML files
    │
    ├─ Email Platform (Port 9000)
    │  └─ Docker Compose
    │     ├─ Listmonk App
    │     └─ PostgreSQL Database
    │
    └─ Tailscale (VPN)
       └─ Encrypted tunnel for remote access
          └─ IP: 100.124.18.6
```

---

## 🎯 What's Running Right Now?

| Service | Port | Status | URL |
|---------|------|--------|-----|
| Website | 8000 | ✅ Running | http://100.124.18.6:8000 |
| Listmonk | 9000 | ✅ Running | http://100.124.18.6:9000 |
| SSH | 22 | ✅ Ready | 100.124.18.6 |
| Tailscale | VPN | ✅ Connected | Private Network |

---

## 🔑 Key Credentials

| What | Value | ⚠️ |
|------|-------|-----|
| Tailscale IP | `100.124.18.6` | Public-ish |
| SSH User | `craftededgesolutions-africa` | Known |
| SSH Password | `7996` | 🔒 SECRET |
| Listmonk Admin | `admin` | Known |
| Listmonk Password | `password` | 🔒 CHANGE ME |
| Sudo Password | `7996` | 🔒 SECRET |

**⚠️ IMPORTANT**: Change Listmonk admin password immediately!

---

## 📂 Project Structure

```
/home/craftededgesolutions-africa/
│
├── craftededgesolutions.africa/          (Main Project)
│   ├── 📖 QUICK_REFERENCE.md            (Start here!)
│   ├── 📖 SYSTEM_STATE.md               (System config)
│   ├── 📖 SSH_SETUP.md                  (SSH guide)
│   ├── 📖 README.md                     (This file)
│   │
│   ├── 🌐 Website Files
│   │   ├── index.html
│   │   ├── services.html
│   │   ├── solutions.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── builder.html
│   │   ├── editor.html
│   │   └── style.css
│   │
│   ├── 📧 Email Platform
│   │   ├── docker-compose.listmonk.yml
│   │   └── listmonk/
│   │       └── config.toml
│   │
│   ├── 📁 Git & Deployment
│   │   ├── .git/
│   │   ├── .github/workflows/
│   │   └── .gitignore
│   │
│   ├── 📁 Assets
│   │   ├── uploads/
│   │   ├── favicon.svg
│   │   ├── robots.txt
│   │   ├── sitemap.xml
│   │   └── llms.txt
│   │
│   └── 🔧 Configuration
│       ├── tweaks-panel.jsx
│       └── style.css
│
├── wellness-solutions.africa/           (Sister project)
├── wsa-roaming-assets/                  (Shared assets)
└── wsa-assets/                          (More assets)
```

---

## 🚀 Common Tasks

### Edit Website
```bash
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
# Edit any .html or .css file
# Refresh browser - changes are live (no restart needed!)
```

### Manage Email Platform
```bash
# Login at: http://100.124.18.6:9000
# Default: admin / password
# Create mailing lists, send campaigns, manage subscribers
```

### Check System Status
```bash
# See all running services
cd /home/craftededgesolutions-africa
cat craftededgesolutions.africa/QUICK_REFERENCE.md
# Or check SYSTEM_STATE.md
```

### Deploy Changes
```bash
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
git add .
git commit -m "describe your changes"
git push origin main
```

### Access from Another Device
1. Install Tailscale: https://tailscale.com/download
2. Authenticate with your account
3. Access: `http://100.124.18.6:8000` (or `:9000`)
4. SSH: `ssh craftededgesolutions-africa@100.124.18.6`

---

## 🔧 Troubleshooting

### Website not loading?
```bash
ps aux | grep "http.server 8000"
# If not found, restart:
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
python3 -m http.server 8000 &
```

### Listmonk not working?
```bash
echo "7996" | sudo -S docker ps
# If stopped, restart:
echo "7996" | sudo -S docker-compose -f craftededgesolutions.africa/docker-compose.listmonk.yml up -d
```

### Can't SSH in?
```bash
# Make sure Tailscale is running:
echo "7996" | sudo -S tailscale status
# Should show this PC (100.124.18.6) as online
```

### Need more help?
- See **SYSTEM_STATE.md** for detailed troubleshooting
- See **SSH_SETUP.md** for SSH issues
- See **QUICK_REFERENCE.md** for common commands

---

## 📊 System Info

| Property | Value |
|----------|-------|
| OS | Ubuntu 24.04 Noble (WSL2) |
| Hostname | meshackvsyouall |
| User | craftededgesolutions-africa |
| Tailscale IP | 100.124.18.6 |
| Docker | 29.4.2 (via Docker Desktop) |
| Python | 3.x |

---

## 🔐 Security Notes

- **Tailscale**: Only accessible to devices in your Tailscale network
- **SSH**: Password protected with `7996` - keep it secret!
- **Listmonk**: Default password - CHANGE IMMEDIATELY!
- **Database**: PostgreSQL only accessible from Docker containers
- **Firewall**: Tailscale provides encryption & access control

---

## 🎯 Development Workflow

```
1. Edit files locally (they auto-reload)
   ↓
2. Test in browser (http://100.124.18.6:8000)
   ↓
3. Commit to git
   ↓
4. Push to GitHub
   ↓
5. GitHub Actions deploy (if configured)
```

---

## 📝 Recent Work (Last 5 commits)

```
960bcf9 feat: add Managed Email Marketing service and Listmonk infrastructure
b0afa5a style: switch heading font from Syne to Montserrat Bold
986ad78 fix: correct builder teaser rendering and style consistency
f40bbf6 feat: add Crafted Builder teaser page, SEO FAQ schema
bac8d2e seo: add structured data, Open Graph, Twitter Cards
```

---

## 🚀 Next Steps

- [ ] Change Listmonk admin password from `password` to something secure
- [ ] Integrate Zoho SMTP with Listmonk for email sending
- [ ] Set up automated database backups
- [ ] Configure GitHub Actions for deployment
- [ ] Add health monitoring/alerting
- [ ] Set up SSL certificates for production

---

## 📞 Quick Links

| Resource | Link |
|----------|------|
| Website | http://100.124.18.6:8000 |
| Listmonk | http://100.124.18.6:9000 |
| GitHub | (check repo settings) |
| Tailscale | https://tailscale.com |
| Docker Docs | https://docs.docker.com |

---

## 💾 Remember

- **Base Path**: `/home/craftededgesolutions-africa/`
- **Always check SYSTEM_STATE.md** for authoritative system info
- **Keep QUICK_REFERENCE.md updated** with your workflows
- **Documentation is in the repo** - commit changes to .md files
- **Tailscale IP is stable** - `100.124.18.6` (unless you leave the network)

---

## 🎓 Knowledge Base

This repo contains living documentation that evolves as the system changes:

- ✅ **QUICK_REFERENCE.md** - Day-to-day commands and workflows
- ✅ **SYSTEM_STATE.md** - Complete system configuration (source of truth)
- ✅ **SSH_SETUP.md** - All SSH access methods and troubleshooting
- ✅ **README.md** - This overview (high-level intro)

**When starting work, read QUICK_REFERENCE.md first. When you need details, check SYSTEM_STATE.md.**

---

*Last Updated: May 9, 2026*  
*For updates, edit this file and commit to git.*  
*All documentation is version-controlled and tracked.*
