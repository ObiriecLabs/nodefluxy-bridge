"""
NODEFLUXY Bridge — ComfyUI custom node
Aggiunge route /nodefluxy/* al server aiohttp di ComfyUI.

Installazione:
    cd ComfyUI/custom_nodes
    git clone https://github.com/ObiriecLabs/nodefluxy-bridge
    # riavvia ComfyUI

Poi in NODEFLUXY: Impostazioni → Bridge URL = http://localhost:8188
"""

from .server import register_routes, load_config

# ComfyUI chiama questo all'avvio
try:
    from server import PromptServer
    register_routes(PromptServer.instance.routes)
    load_config()
    print("\n  ✦ NODEFLUXY Bridge attivo → /nodefluxy/* su porta 8188\n")
except Exception as e:
    print(f"\n  ✦ NODEFLUXY Bridge: errore avvio — {e}\n")

# ComfyUI richiede questi mapping anche se il node non appare nel grafo
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
