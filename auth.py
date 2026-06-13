"""
Gestione API key bridge.
La chiave viene generata al primo avvio e salvata in config.json.
L'utente la copia nelle impostazioni NODEFLUXY una sola volta.
"""

import secrets
import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"
_api_key: str = ""


def load_config() -> dict:
    global _api_key
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            _api_key = cfg.get("api_key", "")
            return cfg
        except Exception:
            pass
    # primo avvio — genera chiave
    _api_key = secrets.token_hex(32)
    cfg = {"api_key": _api_key, "version": "1.0.0"}
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    print(f"\n  ✦ NODEFLUXY Bridge — API Key generata:")
    print(f"    {_api_key}")
    print(f"    Copiala in NODEFLUXY → Impostazioni → Bridge API Key\n")
    return cfg


def verify(request) -> bool:
    key = request.headers.get("X-NODEFLUXY-Key", "")
    return key == _api_key and bool(_api_key)


def get_key() -> str:
    return _api_key
