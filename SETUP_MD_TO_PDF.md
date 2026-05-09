# 📄 Professional MD to PDF Setup Guide

**Goal**: Convert markdown documentation to professional Swiss-style PDFs locally  
**Tools**: Pandoc + Eisvogel Template  
**Time**: 10 minutes  
**Cost**: Free

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Pandoc & Dependencies

```bash
# Update package lists
sudo apt-get update

# Install Pandoc
sudo apt-get install -y pandoc

# Install TeX for PDF output (required for professional formatting)
sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended

# Verify installation
pandoc --version
```

### Step 2: Download Eisvogel Template (Swiss Professional Style)

```bash
# Create templates directory
mkdir -p ~/.pandoc/templates

# Download Eisvogel template
cd ~/.pandoc/templates
wget https://raw.githubusercontent.com/Wandmalfarbe/pandoc-latex-environment/master/eisvogel.latex

# Verify it downloaded
ls -lh eisvogel.latex
```

### Step 3: Create Conversion Script

```bash
# Create a helper script
cat > /usr/local/bin/md2pdf << 'EOF'
#!/bin/bash

# Usage: md2pdf input.md [output.pdf]
INPUT="$1"
OUTPUT="${2:-${INPUT%.md}.pdf}"

if [ ! -f "$INPUT" ]; then
    echo "❌ Error: File not found: $INPUT"
    exit 1
fi

echo "📄 Converting: $INPUT → $OUTPUT"
echo "⏳ Processing..."

pandoc "$INPUT" \
  --template=eisvogel \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --highlight-style=pygments \
  --pdf-engine=xelatex \
  -V mainfont="Helvetica" \
  -V monofont="Monaco" \
  -V geometry:margin=2cm \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue \
  -V lang=en \
  -V table-use-row-colors=true \
  -o "$OUTPUT"

if [ $? -eq 0 ]; then
    echo "✅ Success! Generated: $OUTPUT"
    echo "📊 Size: $(du -h "$OUTPUT" | cut -f1)"
else
    echo "❌ Conversion failed!"
    exit 1
fi
EOF

chmod +x /usr/local/bin/md2pdf
```

### Step 4: Test It!

```bash
# Convert this project's documentation
cd /home/craftededgesolutions-africa/craftededgesolutions.africa

# Convert README
md2pdf README.md README.pdf

# Convert System State
md2pdf SYSTEM_STATE.md SYSTEM_STATE.pdf

# Convert Quick Reference
md2pdf QUICK_REFERENCE.md QUICK_REFERENCE.pdf

# All at once
for file in *.md; do md2pdf "$file"; done
```

---

## 🎨 Customization Options

### Basic Conversion (No Styling)
```bash
pandoc input.md -o output.pdf
```

### Professional (What We Set Up)
```bash
pandoc input.md \
  --template=eisvogel \
  --toc \
  --number-sections \
  -o output.pdf
```

### Custom Styling
```bash
pandoc input.md \
  --template=eisvogel \
  -V title="Project Name" \
  -V author="Your Name" \
  -V date="$(date +%Y-%m-%d)" \
  -V mainfont="Arial" \
  -V fontsize=11pt \
  -V linestretch=1.5 \
  -V geometry:margin=1.5cm \
  --toc \
  --number-sections \
  -o output.pdf
```

### For Client Documents
```bash
pandoc input.md \
  --template=eisvogel \
  -V title="Client Documentation" \
  -V subtitle="Crafted Edge Solutions" \
  -V author="Crafted Edge Solutions Africa" \
  -V date="$(date +%d.%m.%Y)" \
  -V mainfont="Helvetica" \
  -V monofont="Courier New" \
  -V fontsize=11pt \
  -V geometry:margin=2cm \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue \
  --toc \
  --toc-depth=2 \
  --number-sections \
  --highlight-style=pygments \
  -o output.pdf
```

---

## 📋 Advanced: Batch Conversion Script

```bash
cat > /usr/local/bin/md2pdf-all << 'EOF'
#!/bin/bash

# Convert all .md files in a directory to PDF

if [ -z "$1" ]; then
    DIR="."
else
    DIR="$1"
fi

echo "🔄 Converting all .md files in: $DIR"
echo ""

COUNT=0
for file in "$DIR"/*.md; do
    if [ -f "$file" ]; then
        output="${file%.md}.pdf"
        echo "📄 Converting: $(basename "$file")"
        md2pdf "$file" "$output"
        COUNT=$((COUNT + 1))
        echo ""
    fi
done

echo "✅ Done! Converted $COUNT files"
ls -lh "$DIR"/*.pdf 2>/dev/null || echo "No PDFs found"
EOF

chmod +x /usr/local/bin/md2pdf-all

# Usage:
md2pdf-all                                    # Current directory
md2pdf-all /home/craftededgesolutions-africa  # Specific directory
```

---

## 🖼️ Preview Before Converting

```bash
# Install a markdown previewer
sudo apt-get install -y marked  # Or use VS Code

# View in terminal
bat README.md  # Syntax highlighting

# Or use VS Code Markdown Preview (local)
code README.md  # Then Ctrl+Shift+V for preview
```

---

## 💻 Integration with Your Workflow

### Auto-Convert on Save (Watch Mode)

```bash
cat > /usr/local/bin/md2pdf-watch << 'EOF'
#!/bin/bash

# Watch a directory and auto-convert .md to PDF

if [ -z "$1" ]; then
    WATCH_DIR="."
else
    WATCH_DIR="$1"
fi

echo "👀 Watching: $WATCH_DIR"
echo "Press Ctrl+C to stop"

while true; do
    inotifywait -r -e modify "$WATCH_DIR"/*.md 2>/dev/null | while read line; do
        FILE=$(echo "$line" | awk '{print $1}')
        md2pdf "$FILE"
    done
done
EOF

chmod +x /usr/local/bin/md2pdf-watch

# Install inotify-tools first:
sudo apt-get install -y inotify-tools

# Usage:
md2pdf-watch /path/to/docs
```

---

## 📱 Download PDFs to Phone

Once generated, download to your phone:

```bash
# Via SSH (secure tunnel)
scp craftededgesolutions-africa@100.124.18.6:~/docs/*.pdf ~/Downloads/

# Or via Tailscale (if using a file server)
# Place PDFs in web root, access via http://100.124.18.6:8000/docs/

# Or share via terminal
# Generate QR code of file path to share
qrencode -t ansiutf8 "http://100.124.18.6:8000/docs/SYSTEM_STATE.pdf"
```

---

## 🔧 Troubleshooting

### "xelatex not found"
```bash
# Install full LaTeX
sudo apt-get install -y texlive-xetex texlive-fonts-recommended
```

### "eisvogel.latex not found"
```bash
# Verify template location
ls ~/.pandoc/templates/eisvogel.latex

# Or specify full path
pandoc input.md --template=$HOME/.pandoc/templates/eisvogel.latex -o output.pdf
```

### "File is too large" or "Slow conversion"
```bash
# Use simpler template
pandoc input.md --pdf-engine=pdflatex -o output.pdf

# Or convert without table of contents
pandoc input.md --template=eisvogel --toc --number-sections -o output.pdf
```

### Colors/Fonts not showing
```bash
# Ensure full LaTeX is installed
sudo apt-get install -y texlive-full
```

---

## ✅ Verification

```bash
# Test conversion
cd /home/craftededgesolutions-africa/craftededgesolutions.africa
md2pdf README.md TEST.pdf

# Check file was created
ls -lh TEST.pdf

# If you have a PDF viewer installed:
# evince TEST.pdf  (GNOME)
# xpdf TEST.pdf    (Terminal)
```

---

## 📚 Advanced Resources

- **Pandoc Docs**: https://pandoc.org/
- **Eisvogel Template**: https://github.com/Wandmalfarbe/pandoc-latex-environment
- **Markdown Guide**: https://www.markdownguide.org/

---

## 🎯 Quick Reference

```bash
# Convert single file
md2pdf input.md

# Convert with custom output name
md2pdf input.md custom-output.pdf

# Convert all in directory
md2pdf-all /path/to/docs

# Watch directory for changes
md2pdf-watch /path/to/docs
```

---

*Setup Time: ~5 minutes*  
*Tool Cost: Free*  
*Professional Quality: Yes*  
*Battle-Tested: Yes*  
*Suitable for Client Work: Yes*
