"""
NODEFLUXY Bridge — ComfyUI custom node
Aggiunge route /nodefluxy/* al server aiohttp di ComfyUI.

Installazione:
    cd ComfyUI/custom_nodes
    git clone https://github.com/ObiriecLabs/nodefluxy-bridge
    # riavvia ComfyUI

Poi in NODEFLUXY: Impostazioni → Bridge URL = http://localhost:8188
"""

# ComfyUI chiama questo all'avvio
try:
    from .server import register_routes, load_config
    from server import PromptServer
    register_routes(PromptServer.instance.routes)
    load_config()
    print("\n  ✦ NODEFLUXY Bridge attivo → /nodefluxy/* su porta 8188\n")
except Exception as e:
    import traceback
    print(f"\n  ✦ NODEFLUXY Bridge: errore avvio — {e}")
    traceback.print_exc()
    print()

# ComfyUI richiede questi mapping anche se il node non appare nel grafo
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
