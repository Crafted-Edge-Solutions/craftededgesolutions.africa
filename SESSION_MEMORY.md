# 🧠 Session Memory & Context Bank

**Purpose**: Persistent knowledge base for maintaining context between conversations  
**Last Updated**: May 9, 2026  
**Version**: 1.0

---

## 📌 Current Session Context

### What We Just Did (May 9, 2026)
- ✅ Started Listmonk email platform on Docker (port 9000)
- ✅ Installed & authenticated Tailscale (IP: 100.124.18.6)
- ✅ Created comprehensive living documentation (4 files, 1,110 lines)
- ✅ Discussed using this machine as web server
- ✅ Planned local AI models + professional MD to PDF workflow

### Active Projects
1. **Crafted Edge Solutions Website**
   - Status: ✅ Running locally (port 8000)
   - Remote Access: http://100.124.18.6:8000
   - Last Commit: 0016461 (docs)
   - Next: Zoho SMTP integration

2. **Listmonk Email Platform**
   - Status: ✅ Running in Docker (port 9000)
   - Remote Access: http://100.124.18.6:9000
   - Admin: admin / password (⚠️ needs change)
   - Database: PostgreSQL (listmonk_data volume)

---

## 🎯 Key Decisions Made

### Architecture Decision: Development vs Production
- **Development**: This WSL2 machine (stable for testing)
- **Production**: Deploy to Netlify/Vercel (reliable, free tier)
- **Staging**: Accessible via Tailscale at 100.124.18.6
- **Rationale**: Home internet/WSL2 not ideal for 24/7 production

### Tools Selected
- **MD to PDF**: Pandoc + Eisvogel template (professional, free, battle-tested)
- **Local AI**: Ollama with Mistral 7B (lightweight, runs locally)
- **Documentation**: Living docs in git (version controlled, always available)

### Infrastructure Choices
- **VPN**: Tailscale (encrypted, secure, private network)
- **Email**: Listmonk self-hosted (control over data, can integrate Zoho SMTP)
- **Website**: Static HTML (fast, simple, easy to deploy anywhere)
- **Hosting**: Docker Compose (reproducible, portable)

---

## 🔑 Critical Credentials & Access Points

### Tailscale
- **IP**: 100.124.18.6 (stable, fixed reference point)
- **Status**: ✅ Connected & authenticated
- **Account**: meshackmogire406@
- **Usage**: Remote access, secure tunnel

### SSH Access
- **Host**: craftededgesolutions-africa@100.124.18.6
- **Password**: 7996
- **Port**: 22 (default)
- **Method**: Password auth (key auth documented in SSH_SETUP.md)
- **When to Use**: Running commands remotely, file transfer, debugging

### Services
| Service | Local | Remote | Credentials |
|---------|-------|--------|-------------|
| Website | localhost:8000 | 100.124.18.6:8000 | None |
| Listmonk | localhost:9000 | 100.124.18.6:9000 | admin/password |
| SSH | N/A | 100.124.18.6:22 | user/7996 |
| Database | 5432 (internal) | Docker network | listmonk/listmonk |

### Sudo/Root
- **Password**: 7996
- **Usage**: Docker commands, system administration
- **Prefix**: `echo "7996" | sudo -S`

---

## 📚 Documentation Map

| File | Purpose | When to Read | Size |
|------|---------|--------------|------|
| **README.md** | High-level overview | First time / refresher | 8.2K |
| **QUICK_REFERENCE.md** | Daily commands | Daily development | 7.4K |
| **SYSTEM_STATE.md** | Complete config (authoritative) | Need detailed info | 6.8K |
| **SSH_SETUP.md** | SSH access guide | Setting up remote access | 6.6K |
| **SESSION_MEMORY.md** | This file (context bank) | Between sessions | (dynamic) |

**How to Use**:
1. Start session: Read README.md (5 min)
2. Developing: Reference QUICK_REFERENCE.md
3. Need details: Check SYSTEM_STATE.md
4. Remote access issues: See SSH_SETUP.md
5. Context: Check this file

---

## 🔄 Common Workflows

### Daily Development
```bash
# 1. Verify services
curl http://localhost:8000
curl http://localhost:9000

# 2. Make changes
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
# Edit HTML/CSS files

# 3. Test in browser
# Changes auto-reload (static server)

# 4. Commit
git add .
git commit -m "describe changes"
git push
```

### Remote Work (From Another Device)
```bash
# 1. Ensure Tailscale is running on both machines
tailscale status

# 2. SSH in
ssh craftededgesolutions-africa@100.124.18.6

# 3. Work as normal
cd craftededgesolutions.africa
git status
```

### Email Campaign Testing
```bash
# 1. Access Listmonk
http://100.124.18.6:9000

# 2. Login: admin/password

# 3. Create mailing list
# 4. Add subscribers
# 5. Create campaign
# 6. Set up Zoho SMTP (next step)
```

---

## ⚠️ Known Issues & Fixes

### Listmonk Shows "Unhealthy"
- **Cause**: Database connection flakiness
- **Fix**: `docker-compose restart`
- **Prevention**: Keep Docker Desktop running

### Can't SSH In
- **Cause**: Tailscale not connected
- **Fix**: `tailscale status` (should show this PC online)
- **Debug**: Check Tailscale on both machines

### Website Changes Not Showing
- **Cause**: Browser cache
- **Fix**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- **Or**: Clear browser cache

### Docker Permission Denied
- **Cause**: User not in docker group
- **Fix**: Use `echo "7996" | sudo -S docker` prefix
- **Better**: Add user to docker group (requires logout)

---

## 🚀 Next Steps (Prioritized)

### Immediate (Do Soon)
- [ ] Change Listmonk admin password from "password"
- [ ] Install & test Pandoc + Eisvogel for documentation
- [ ] Install Ollama with Mistral 7B model
- [ ] Create MD to PDF conversion script

### Short Term (Next Session)
- [ ] Integrate Zoho SMTP with Listmonk
- [ ] Set up SSH key-based authentication
- [ ] Create automated backup script for database
- [ ] Test converting all .md docs to professional PDFs

### Medium Term (Planning)
- [ ] Configure GitHub Actions for CI/CD
- [ ] Set up monitoring/health checks
- [ ] Plan production deployment strategy
- [ ] Document deployment process

### Long Term (Future)
- [ ] Migrate to production hosting
- [ ] Set up SSL/HTTPS everywhere
- [ ] Implement automated testing
- [ ] Add analytics & monitoring

---

## 💡 Patterns & Lessons Learned

### What Works Well
- ✅ Static HTML + Python server = Fast development cycle
- ✅ Docker Compose for reproducible environments
- ✅ Tailscale for secure private network access
- ✅ Living documentation in git (always accessible)
- ✅ Markdown-based docs (version controllable, portable)

### What to Avoid
- ❌ Trying to run production on home internet + WSL2
- ❌ Hardcoding credentials in scripts
- ❌ Not committing documentation changes
- ❌ Using default passwords in production
- ❌ Relying on manual memory (use docs!)

### Best Practices Established
- 📝 All documentation in repo
- 🔐 Separate dev/staging/production
- 🐳 Docker for reproducibility
- 📊 Session memory for context persistence
- 🔄 Living docs that evolve with system

---

## 🔐 Security Checklist

- [ ] Change Listmonk admin password
- [ ] Use SSH keys instead of password (optional)
- [ ] Never hardcode 7996 in scripts
- [ ] Keep Tailscale network private
- [ ] Regular git commits (audit trail)
- [ ] No credentials in git repos
- [ ] Firewall enabled (Tailscale provides this)

---

## 📞 Quick Reference

### Emergency Commands
```bash
# Is website running?
ps aux | grep http.server | grep -v grep

# Is Listmonk running?
echo "7996" | sudo -S docker ps

# SSH from anywhere
ssh craftededgesolutions-africa@100.124.18.6

# View all docs
cat README.md
```

### File Locations
```
/home/craftededgesolutions-africa/        (base)
/home/craftededgesolutions-africa/craftededgesolutions.africa/   (project)
/home/craftededgesolutions-africa/craftededgesolutions.africa/.git/  (git repo)
```

### Service Ports
```
8000  = Website server
9000  = Listmonk
5432  = PostgreSQL (internal Docker)
22    = SSH
```

---

## 🎓 To Remember for Next Session

1. **Tailscale IP is your access point**: 100.124.18.6
2. **Read README.md first** to refresh context
3. **Check QUICK_REFERENCE.md** for common commands
4. **SYSTEM_STATE.md is the source of truth** for configuration
5. **Documentation is in git** - commit changes!
6. **Services auto-start** on system boot? (check this)
7. **Always use sudo password prefix** for root commands

---

## 📝 Session Handoff Notes

**For Next Conversation**:
- System is stable and well-documented
- Services are running and accessible
- Tailscale provides secure remote access
- All docs are version controlled in git
- Ready for: Zoho SMTP integration, PDF documentation setup, local AI models
- PC needs: Ollama + lightweight model, Pandoc setup, MD→PDF workflow

**If You're Reading This**:
- You've built a solid development foundation
- Documentation is comprehensive and organized
- Everything is accessible via Tailscale
- You can work from anywhere
- Living docs will help you remember context

**Next priorities** (from your requirements):
1. Professional MD→PDF workflow (Pandoc ready)
2. Local AI models (Ollama planned)
3. Update this memory file after each session

---

*Last Updated: May 9, 2026*  
*Next Update: After Zoho integration & tool setup*  
*Maintainer: You (update with new learnings)*
