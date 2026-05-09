# 🚀 Quick Reference & Dev Handbook

**Project**: Crafted Edge Solutions Africa  
**System**: WSL2 Ubuntu on Windows  
**Last Updated**: May 9, 2026

---

## 🎯 In One Sentence

> **Running a static website + Listmonk email platform locally on WSL2, accessible via Tailscale at 100.124.18.6**

---

## 📍 Where Everything Is

```
BASE PATH: /home/craftededgesolutions-africa/

craftededgesolutions.africa/
├── 📄 SYSTEM_STATE.md          ← Full system state (read this first)
├── 📄 SSH_SETUP.md              ← SSH access guide
├── 📄 QUICK_REFERENCE.md        ← This file
├── 🌐 Website (Python server)   ← Port 8000
├── 📧 Email Platform (Docker)   ← Port 9000
└── 📁 Project files (HTML/CSS/JS)
```

---

## 🔌 Access Points

### Local Machine
- Website: `http://localhost:8000`
- Listmonk: `http://localhost:9000`
- SSH: (N/A, you're already here)

### Remote/Tailscale
- Website: `http://100.124.18.6:8000`
- Listmonk: `http://100.124.18.6:9000`
- SSH: `ssh craftededgesolutions-africa@100.124.18.6`

### Credentials
| What | Value |
|------|-------|
| Tailscale IP | `100.124.18.6` |
| SSH User | `craftededgesolutions-africa` |
| SSH Password | `7996` |
| Listmonk Admin | `admin` / `password` |
| Sudo Password | `7996` |

---

## 🎮 Control Everything

### Start Website Server
```bash
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
python3 -m http.server 8000 &
```

### Start Listmonk (Docker)
```bash
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
echo "7996" | sudo -S docker-compose -f docker-compose.listmonk.yml up -d
```

### Check All Services
```bash
# Website
curl http://localhost:8000

# Listmonk
curl http://localhost:9000

# Docker containers
echo "7996" | sudo -S docker ps

# Tailscale
echo "7996" | sudo -S tailscale status
```

### Stop Everything
```bash
# Website
pkill -f "http.server 8000"

# Listmonk
echo "7996" | sudo -S docker-compose -f /home/craftededgesolutions-africa/craftededgesolutions.africa/docker-compose.listmonk.yml down
```

---

## 📂 Key Files to Know

| File | Purpose | Edit? |
|------|---------|-------|
| `index.html` | Homepage | Yes |
| `services.html` | Services page | Yes |
| `contact.html` | Contact form | Yes |
| `style.css` | Global styles | Yes |
| `docker-compose.listmonk.yml` | Email service config | Rarely |
| `listmonk/config.toml` | Listmonk settings | Rarely |

---

## 🔄 Development Workflow

### Check Current State
```bash
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
git status
```

### Make Changes
```bash
# Edit HTML/CSS files
# They'll auto-reload in browser (since it's a static server)
```

### Save to Git
```bash
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
git add .
git commit -m "describe changes"
git push origin main
```

### View Recent Commits
```bash
git log --oneline -10
```

---

## 🚨 Common Tasks

### Task: Update Website
1. Edit `.html` or `.css` files in `craftededgesolutions.africa/`
2. Refresh browser at `http://100.124.18.6:8000`
3. Commit to git

### Task: Access Listmonk
1. Go to `http://100.124.18.6:9000`
2. Login: `admin` / `password`
3. Create mailing lists, send campaigns, manage subscribers

### Task: SSH from Another Device
```bash
ssh craftededgesolutions-africa@100.124.18.6
# password: 7996
```

### Task: Execute Command Remotely
```bash
ssh craftededgesolutions-africa@100.124.18.6 'docker ps'
ssh craftededgesolutions-africa@100.124.18.6 'curl http://localhost:9000'
```

### Task: Copy Files To/From Remote
```bash
# Upload
scp local-file.txt craftededgesolutions-africa@100.124.18.6:~/

# Download
scp craftededgesolutions-africa@100.124.18.6:~/remote-file.txt ./
```

### Task: View Logs
```bash
# Website server logs
tail -f /tmp/http-server.log

# Listmonk app logs
echo "7996" | sudo -S docker-compose -f craftededgesolutions.africa/docker-compose.listmonk.yml logs -f app

# Database logs
echo "7996" | sudo -S docker-compose -f craftededgesolutions.africa/docker-compose.listmonk.yml logs -f db
```

### Task: Restart a Service
```bash
# Restart Listmonk
echo "7996" | sudo -S docker-compose -f craftededgesolutions.africa/docker-compose.listmonk.yml restart

# Restart Website
pkill -f "http.server 8000"
cd craftededgesolutions.africa && python3 -m http.server 8000 &
```

---

## 💡 Pro Tips

### Alias for SSH
Add to your `~/.bash_profile` or `~/.zshrc`:
```bash
alias meshack='ssh craftededgesolutions-africa@100.124.18.6'
alias meshack-web='ssh craftededgesolutions-africa@100.124.18.6 -L 8000:localhost:8000'
alias meshack-mail='ssh craftededgesolutions-africa@100.124.18.6 -L 9000:localhost:9000'
```

Then simply:
```bash
meshack          # SSH in
meshack-web      # Tunnel website locally
meshack-mail     # Tunnel email locally
```

### Quick Status Check
```bash
cd /home/craftededgesolutions-africa && echo "=== WEBSITE ===" && \
ps aux | grep "http.server" | grep -v grep && echo "✓ Running" || echo "✗ Stopped" && \
echo "=== LISTMONK ===" && echo "7996" | sudo -S docker ps --format "table {{.Names}}\t{{.Status}}" | grep listmonk
```

### Monitor Everything
```bash
watch -n 2 "echo '=== Services ===' && ps aux | grep http.server | grep -v grep && echo '7996' | sudo -S docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

---

## 🔐 Security Reminders

- **Sudo Password**: `7996` - Don't hardcode in scripts!
- **Listmonk Password**: Change `password` immediately!
- **SSH Key**: Keep private key in `~/.ssh/` with `chmod 600`
- **Tailscale**: Only people on your Tailscale network can access
- **Database**: PostgreSQL only accessible from within Docker network

---

## 📊 System Health Checklist

Run this occasionally:

```bash
echo "=== SYSTEM STATE ===" && \
echo "1. Tailscale:" && echo "7996" | sudo -S tailscale status --self && \
echo "" && echo "2. Docker Containers:" && echo "7996" | sudo -S docker ps && \
echo "" && echo "3. Website Server:" && ps aux | grep "http.server" | grep -v grep && \
echo "" && echo "4. Disk Usage:" && df -h / && \
echo "" && echo "5. Memory:" && free -h
```

---

## 🔧 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| "Connection refused" | Restart Tailscale: `sudo tailscale down && sudo tailscale up` |
| Listmonk unhealthy | Restart: `docker-compose -f ... restart` |
| Website not loading | Check: `ps aux \| grep http.server` |
| Can't SSH in | Verify: `tailscale status` (must show this PC online) |
| Docker not working | Start Docker Desktop on Windows |
| Sudo asks for password | Use: `echo "7996" \| sudo -S command` |

---

## 📚 Documentation Files

- **SYSTEM_STATE.md** - Detailed system configuration and status
- **SSH_SETUP.md** - Complete SSH access guide
- **QUICK_REFERENCE.md** - This file (quick access)

**Always start with SYSTEM_STATE.md for full context.**

---

## 🎯 What's Next?

- [ ] Change Listmonk admin password
- [ ] Integrate Zoho SMTP with Listmonk
- [ ] Set up automated database backups
- [ ] Configure GitHub Actions for CI/CD
- [ ] Add monitoring/alerting
- [ ] Set up SSL certificates

---

## 👤 Key Contacts/Accounts

| Service | Email | Status |
|---------|-------|--------|
| Tailscale | meshackmogire406@ | ✅ Active |
| GitHub | (check repo) | ✅ Active |
| Zoho | (check with you) | ⚠️ Pending |
| Listmonk Admin | admin@... | ⚠️ Default password |

---

*This is a living document. Keep it updated as the system evolves.*  
*When in doubt, check SYSTEM_STATE.md for authoritative info.*
