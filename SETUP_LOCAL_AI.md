# 🤖 Local AI Models Setup Guide

**Goal**: Run AI models locally on your PC (no cloud, no API calls)  
**Tool**: Ollama  
**Models**: Mistral 7B (recommended), Phi, Neural-Chat  
**Cost**: Free  
**Time**: 15 minutes + model download

---

## 🚀 Quick Setup

### Step 1: Install Ollama on WSL2

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Expected output: ollama version X.X.X
```

### Step 2: Start Ollama Service

```bash
# Start the Ollama daemon in background
ollama serve &

# Or run in foreground to see logs:
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Step 3: Pull a Model

**Recommended: Mistral 7B** (Best balance of speed and quality)

```bash
# Download Mistral model
ollama pull mistral

# This will take 5-10 minutes (4.1 GB download)
# Progress will show: Pulling manifest... Pulling layers... Done!
```

### Step 4: Run Your First AI Query

```bash
# Start interactive chat
ollama run mistral

# Then type your question:
# > Explain what Tailscale is in one sentence
# > How do I set up SSH keys?
# > What's the best way to document a system?

# Press Ctrl+D to exit
```

---

## 🤖 Available Models (For Your PC)

### Lightweight & Fast (Recommended)

| Model | Size | Speed | Quality | RAM | Use Case |
|-------|------|-------|---------|-----|----------|
| **Phi** | 2.7B | ⚡⚡ Fastest | ⭐⭐⭐ | 3GB | Quick questions |
| **Orca Mini** | 3B | ⚡⚡ Very Fast | ⭐⭐⭐ | 4GB | General tasks |
| **Mistral** | 7B | ⚡ Fast | ⭐⭐⭐⭐ | 8GB | Best choice |
| **Neural-Chat** | 7B | ⚡ Fast | ⭐⭐⭐ | 8GB | Conversations |

### Powerful (If You Have RAM)

| Model | Size | Speed | Quality | RAM | Use Case |
|-------|------|-------|---------|-----|----------|
| **Dolphin Mixtral** | 8x7B | Slow | ⭐⭐⭐⭐⭐ | 40GB | Complex tasks |
| **Llama 2** | 7B-13B | Medium | ⭐⭐⭐⭐ | 16GB | Good all-rounder |

### For Your Setup: **Use Mistral** ✅

```bash
# Pull Mistral (7B, best all-arounder)
ollama pull mistral
```

---

## 💻 Usage Examples

### 1. Help with Documentation

```bash
# Ask AI to improve your documentation
ollama run mistral << 'EOF'
Improve this markdown for clarity and professionalism:

## SSH Setup

Users can SSH into the system using:
ssh craftededgesolutions-africa@100.124.18.6

The password is 7996. SSH keys can also be used.

Provide a cleaner version.
EOF
```

### 2. Code Review/Debugging

```bash
# Get help with a script
ollama run mistral << 'EOF'
Review this bash script for issues:

#!/bin/bash
for file in *.md; do
    pandoc "$file" -o "${file%.md}.pdf"
done

What improvements would you suggest?
EOF
```

### 3. System Architecture Advice

```bash
# Ask about your setup
ollama run mistral << 'EOF'
Is it a good idea to run a production website on WSL2?
What are the pros and cons compared to cloud hosting?
EOF
```

### 4. Quick Questions

```bash
# One-liner help
echo "How do I list Docker containers?" | ollama run mistral
echo "What's the difference between SSH keys and passwords?" | ollama run mistral
echo "Explain Tailscale in simple terms" | ollama run mistral
```

### 5. Generate Documentation

```bash
# Auto-generate a section
ollama run mistral << 'EOF'
Generate a troubleshooting section for this system:
- Listmonk email platform running on Docker
- Tailscale VPN for remote access
- Website server on Python
- PostgreSQL database

Include common issues and fixes.
EOF
```

---

## 🛠️ Helper Scripts

### Create an `ask-ai` Alias

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ask-ai='ollama run mistral'

# Usage:
ask-ai "How do I backup a PostgreSQL database?"
ask-ai "What's the best way to organize documentation?"
```

### Create a Question File Reader

```bash
cat > /usr/local/bin/ask-file << 'EOF'
#!/bin/bash

# Ask AI about a file's contents

if [ -z "$1" ]; then
    echo "Usage: ask-file <file> <question>"
    echo "Example: ask-file config.toml 'What settings are important?'"
    exit 1
fi

FILE="$1"
QUESTION="${2:-Explain this file}"

if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    exit 1
fi

echo "🤖 Analyzing: $FILE"
echo "❓ Question: $QUESTION"
echo ""

ollama run mistral << EOF
File: $FILE
Contents:
\`\`\`
$(cat "$FILE")
\`\`\`

$QUESTION
EOF
EOF

chmod +x /usr/local/bin/ask-file

# Usage:
ask-file /home/craftededgesolutions-africa/craftededgesolutions.africa/docker-compose.listmonk.yml \
  "What does this Docker Compose file do?"
```

### Batch AI Processing

```bash
cat > /usr/local/bin/ai-batch << 'EOF'
#!/bin/bash

# Process a file line-by-line with AI

FILE="$1"
MODEL="${2:-mistral}"

while IFS= read -r line; do
    if [ -n "$line" ]; then
        echo "❓ $line"
        echo "$line" | ollama run "$MODEL"
        echo ""
    fi
done < "$FILE"
EOF

chmod +x /usr/local/bin/ai-batch
```

---

## 🔧 Advanced: API Mode

### Use Ollama as a REST API

```bash
# Ollama runs an API on localhost:11434
# You can curl it directly:

# Get available models
curl http://localhost:11434/api/tags

# Generate text via API
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "Explain Docker in one sentence",
    "stream": false
  }'
```

### Use with Python

```bash
# Install requests library
pip install requests

# Create a Python script
cat > ai_helper.py << 'EOF'
import requests
import json

def ask_ai(question, model="mistral"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": question, "stream": False}
    )
    return response.json()["response"]

# Usage
answer = ask_ai("What is Tailscale?")
print(answer)
EOF

python ai_helper.py
```

### Integration with Development Tools

```bash
# Use in VS Code terminal
# Use in documentation generation scripts
# Use in deployment automation
# Use in automated testing

# Example: Auto-improve commit messages
git add .
DESCRIPTION=$(ask-ai "Summarize these changes: $(git diff --cached --stat)")
git commit -m "$DESCRIPTION"
```

---

## 📊 Model Performance on Your PC

### Expected Performance (8GB RAM + Mistral)
- **Response time**: 10-30 seconds for typical questions
- **Throughput**: ~20 tokens/second
- **Memory usage**: ~6-7 GB
- **CPU usage**: Will spike during generation

### Tips for Better Performance

```bash
# 1. Close other applications
# Ollama needs RAM and CPU

# 2. Use Phi if Mistral is too slow
ollama pull phi
ollama run phi

# 3. Ask shorter questions for faster responses
# Instead of: "Write a comprehensive guide to..."
# Try: "Summarize Docker in 2 sentences"

# 4. Keep models in memory (they stay loaded after first run)
# First run: ~30s, Subsequent runs: ~10s
```

---

## 🎯 Use Cases for Your System

### 1. **Documentation Help**
```bash
ask-ai "How should I structure system documentation?"
ask-ai "Improve this README section: [paste]"
ask-ai "Generate a troubleshooting guide for: [topic]"
```

### 2. **Code & Config Review**
```bash
ask-file docker-compose.listmonk.yml "Is this configuration correct?"
ask-file style.css "Can you improve this CSS?"
ask-file .bashrc "Are there any security issues?"
```

### 3. **System Administration**
```bash
ask-ai "How do I monitor Docker container health?"
ask-ai "What's the best backup strategy for PostgreSQL?"
ask-ai "How to optimize WSL2 performance?"
```

### 4. **Learning & Training**
```bash
ask-ai "Explain how Tailscale VPN works"
ask-ai "What's the difference between SSH keys and passwords?"
ask-ai "How does Docker Compose work?"
```

### 5. **Writing & Documentation**
```bash
ask-ai "Improve this sentence: [text]"
ask-ai "Generate 5 troubleshooting tips for [topic]"
ask-ai "Create a quick start guide for [topic]"
```

---

## 🔐 Privacy & Data

**Important**: All processing happens locally on your machine!

```bash
# No data leaves your PC
# No API calls made
# No cloud services used
# Your data stays private
# Perfect for sensitive work
```

---

## 📝 Update SESSION_MEMORY.md with Learnings

After using the model, add insights to your session memory:

```markdown
## AI Model Insights (From Ollama Sessions)

### What Worked Well
- Mistral 7B is great for documentation help
- Average response time: 20 seconds
- Good at explaining technical concepts

### What to Improve
- Keep questions focused for faster responses
- Use bullet points in prompts for clarity
- Close other apps for better performance

### Useful Prompts (Save These!)
- "Improve this [markdown/code] for clarity"
- "Summarize in 2 sentences: [text]"
- "Review this configuration for security issues"
```

---

## 🚀 Getting Started

### Recommended First Session

```bash
# 1. Start Ollama
ollama serve &

# 2. Pull Mistral (takes ~10 min)
ollama pull mistral

# 3. Try these questions
ollama run mistral
> What is Tailscale and why use it?
> How should I organize a development system?
> Explain Docker in simple terms
> Ctrl+D to exit
```

---

## 📚 Resources

- **Ollama Docs**: https://ollama.ai/
- **Model Library**: https://ollama.ai/library
- **GitHub**: https://github.com/ollama/ollama

---

*Setup Time: 15 minutes + model download*  
*Cost: Free*  
*Privacy: 100% local*  
*Suitable for: Documentation, learning, coding, system admin*
