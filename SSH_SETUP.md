# SSH Access Guide - Crafted Edge Solutions Dev Environment

**Machine**: meshackvsyouall (WSL2 Ubuntu)  
**Tailscale IP**: `100.124.18.6`  
**User**: `craftededgesolutions-africa`

---

## 🚀 Quick Start (One-Liner)

```bash
ssh craftededgesolutions-africa@100.124.18.6
```

Then enter password when prompted, or use SSH key (see below).

---

## ✅ Prerequisites

1. **Tailscale Connected**: Device must be on the same Tailscale network
   - Download: https://tailscale.com/download
   - Authenticate with your account
   - Verify: `tailscale ip`

2. **SSH Client Installed**:
   - Linux/Mac: Built-in
   - Windows: Use Windows Terminal or `ssh` from WSL/Git Bash
   - PuTTY: Download from https://www.putty.org/

---

## 🔐 Method 1: SSH with Password (Simple)

### Quick Access
```bash
ssh craftededgesolutions-africa@100.124.18.6
# Password: (prompt appears)
```

### Access Services After SSH
```bash
# In your remote terminal:
curl http://localhost:8000    # Check website
curl http://localhost:9000    # Check Listmonk
docker ps                      # View containers (needs sudo)
```

---

## 🔑 Method 2: SSH Key (Recommended for Automation)

### Step 1: Generate SSH Key (on your local machine)

```bash
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/meshack_key
# Press Enter twice (no passphrase needed for automation)
```

This creates:
- `~/.ssh/meshack_key` (private key - keep secret!)
- `~/.ssh/meshack_key.pub` (public key - copy to server)

### Step 2: Add Key to Remote Server

**Option A: Copy-Paste Method**

1. Display your public key:
```bash
cat ~/.ssh/meshack_key.pub
```

2. SSH into the remote machine (password method):
```bash
ssh craftededgesolutions-africa@100.124.18.6
# Enter password: 7996
```

3. Add your key to authorized_keys:
```bash
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

**Option B: SSH-Copy-ID (Easier)**

```bash
ssh-copy-id -i ~/.ssh/meshack_key craftededgesolutions-africa@100.124.18.6
# Enter password when prompted: 7996
```

### Step 3: Test Passwordless SSH

```bash
ssh -i ~/.ssh/meshack_key craftededgesolutions-africa@100.124.18.6
# Should log in without password prompt
```

### Step 4: Create Config File (Optional but Recommended)

Create `~/.ssh/config`:

```
Host meshack-dev
    HostName 100.124.18.6
    User craftededgesolutions-africa
    IdentityFile ~/.ssh/meshack_key
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
```

Then simply:
```bash
ssh meshack-dev
```

---

## 📱 SSH on Different Platforms

### **Windows Terminal / PowerShell**
```powershell
ssh craftededgesolutions-africa@100.124.18.6
```

### **Windows (PuTTY)**
1. Open PuTTY
2. Host: `100.124.18.6`
3. Port: `22`
4. Connection > SSH > Auth > Private Key: `meshack_key.ppk` (convert with PuTTYgen)
5. Click Open

### **macOS Terminal**
```bash
ssh craftededgesolutions-africa@100.124.18.6
```

### **Linux Terminal**
```bash
ssh craftededgesolutions-africa@100.124.18.6
```

### **Mobile (Android/iOS)**
Use **Termux** (Android) or **SSH Files** (iOS):
1. Install SSH app from app store
2. Add host: `100.124.18.6`
3. Username: `craftededgesolutions-africa`
4. Password: `7996`

---

## 🛠️ Common SSH Operations

### Upload File to Remote
```bash
scp ./local-file.txt craftededgesolutions-africa@100.124.18.6:~/
```

### Download File from Remote
```bash
scp craftededgesolutions-africa@100.124.18.6:~/remote-file.txt ./
```

### Execute Remote Command Without Login
```bash
ssh craftededgesolutions-africa@100.124.18.6 'docker ps'
ssh craftededgesolutions-africa@100.124.18.6 'curl http://localhost:9000'
```

### Keep SSH Connection Alive (Tunnel)
```bash
ssh -N -L 8000:localhost:8000 craftededgesolutions-africa@100.124.18.6
# Now access localhost:8000 and it tunnels to remote server
```

### Create Remote Tunnel (Access remote services locally)
```bash
ssh -N -L 9000:localhost:9000 craftededgesolutions-africa@100.124.18.6
# Now visit http://localhost:9000 to access remote Listmonk
```

---

## 🔧 Troubleshooting

### "Connection refused" or "Host unreachable"
- **Check**: Is Tailscale running on both machines?
  ```bash
  tailscale status
  ```
- **Check**: Is the remote machine online?
  - See other devices in `tailscale status` output
- **Fix**: Restart Tailscale
  ```bash
  sudo tailscale down
  sudo tailscale up
  ```

### "Permission denied (publickey)"
- **Issue**: SSH key not properly configured
- **Fix**: Use password method instead, or re-run `ssh-copy-id`

### "Connection timeout"
- **Issue**: Firewall blocking SSH
- **Check**: Make sure SSH service is running on remote
  ```bash
  echo "7996" | sudo -S systemctl status ssh
  ```

### "ssh: command not found" (Windows)
- **Fix**: Use Windows Terminal instead of old CMD
- Or: Install Git for Windows (includes ssh)

---

## 🔐 Security Best Practices

### DO:
- ✅ Use SSH keys instead of passwords
- ✅ Keep private keys in `~/.ssh/` with `chmod 600`
- ✅ Use a firewall (Tailscale already provides one)
- ✅ Rotate keys periodically
- ✅ Use strong passphrases on SSH keys

### DON'T:
- ❌ Share private keys
- ❌ Commit SSH keys to git
- ❌ Use same SSH key for multiple systems
- ❌ Leave SSH key passphrase weak
- ❌ Accept warnings about host key changes without verification

---

## 📋 One-Time Setup Checklist

- [ ] Tailscale installed and authenticated on your machine
- [ ] SSH client available
- [ ] Generated SSH key (if using key auth)
- [ ] Added public key to `~/.ssh/authorized_keys` on remote
- [ ] Tested connection: `ssh craftededgesolutions-africa@100.124.18.6`
- [ ] Created `~/.ssh/config` entry for easy access
- [ ] Verified you can run remote commands: `ssh meshack-dev 'docker ps'`

---

## 💾 Reference

| Command | Purpose |
|---------|---------|
| `ssh user@host` | Connect to remote |
| `ssh-keygen` | Generate SSH key pair |
| `ssh-copy-id` | Copy public key to remote |
| `scp file user@host:~` | Copy file to remote |
| `ssh -i key user@host` | Use specific key |
| `ssh-add ~/.ssh/key` | Add key to agent |
| `ssh-keyscan host >> ~/.ssh/known_hosts` | Pre-approve host key |
| `ssh -v user@host` | Verbose (debug) mode |

---

## 🚀 Next: Claude Code Integration

Once SSH is working:

1. **In Claude Code**, configure remote host:
```json
{
  "remote": "craftededgesolutions-africa@100.124.18.6",
  "key": "/path/to/meshack_key"
}
```

2. **Execute commands** on remote:
```bash
ssh meshack-dev 'cd craftededgesolutions.africa && git status'
```

3. **Edit files** remotely:
```bash
code remote://meshack-dev/home/craftededgesolutions-africa/
```

---

*Last Updated: May 9, 2026*  
*For questions, see SYSTEM_STATE.md*
