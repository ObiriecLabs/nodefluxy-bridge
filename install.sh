#!/bin/bash
# NODEFLUXY Bridge — Installer
# Uso: bash install.sh /path/to/ComfyUI
# Oppure senza argomento per rilevamento automatico

set -e

BRIDGE_REPO="https://github.com/ObiriecLabs/nodefluxy-bridge"
TARGET_DIR=""

# rilevamento automatico percorso ComfyUI
detect_comfyui() {
    local candidates=(
        "$HOME/ComfyUI"
        "$HOME/Desktop/ComfyUI"
        "/opt/ComfyUI"
        "/Volumes/ComfyUI_6TB/ComfyUI"
    )
    for d in "${candidates[@]}"; do
        if [ -f "$d/main.py" ]; then
            echo "$d"
            return
        fi
    done
    echo ""
}

if [ -n "$1" ]; then
    TARGET_DIR="$1/custom_nodes"
else
    COMFYUI=$(detect_comfyui)
    if [ -z "$COMFYUI" ]; then
        echo "❌ ComfyUI non trovato. Specifica il percorso:"
        echo "   bash install.sh /path/to/ComfyUI"
        exit 1
    fi
    TARGET_DIR="$COMFYUI/custom_nodes"
fi

DEST="$TARGET_DIR/nodefluxy_bridge"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  NODEFLUXY Bridge — Installer v1.0  ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  Destinazione: $DEST"
echo ""

if [ -d "$DEST" ]; then
    echo "  ↻ Bridge già installato — aggiorno..."
    git -C "$DEST" pull --rebase
else
    git clone "$BRIDGE_REPO" "$DEST"
fi

echo ""
echo "  ✅ NODEFLUXY Bridge installato."
echo ""
echo "  Prossimi passi:"
echo "  1. Riavvia ComfyUI"
echo "  2. Cerca la riga '✦ NODEFLUXY Bridge attivo' nel log di ComfyUI"
echo "  3. Copia la API Key mostrata nel log"
echo "  4. In NODEFLUXY → Impostazioni → incolla la API Key"
echo ""
