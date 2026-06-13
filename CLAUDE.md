# NODEFLUXY-BRIDGE — CLAUDE.md

## Identità del progetto

| Campo | Valore |
|---|---|
| **Nome** | NODEFLUXY Bridge |
| **Tipo** | ComfyUI custom node (Python) |
| **Repo** | github.com/ObiriecLabs/nodefluxy-bridge (PUBBLICO) |
| **Installazione** | `cd ComfyUI/custom_nodes && git clone ... nodefluxy_bridge` |
| **Status** | v1.0.0 — LIVE |

## Cosa fa

Aggiunge route HTTP + WebSocket `/nodefluxy/*` al server aiohttp di ComfyUI.
NODEFLUXY usa questi endpoint per inviare workflow, monitorare progresso
e recuperare output senza aprire l'interfaccia ComfyUI.

## File chiave

```
nodefluxy-bridge/            (root repo = directory clonata in custom_nodes/nodefluxy_bridge)
├── __init__.py              # entry point ComfyUI — register_routes + load_config
├── auth.py                  # API key: genera al primo avvio, verifica X-NODEFLUXY-Key header
├── comfyui_client.py        # client aiohttp → /prompt, /history, /interrupt, /upload, WS
├── server.py                # 9 handler aiohttp: ping, key, execute, status, outputs, cancel, upload, events WS
├── install.sh               # installer automatico: rilevamento ComfyUI, git clone/pull
├── README.md
└── .gitignore               # esclude config.json (contiene API key)
```

## Regole operative

- **config.json** contiene la API key — NON committare mai, già in .gitignore
- **Nomi directory**: ComfyUI usa il nome dir come modulo Python → deve essere `nodefluxy_bridge` (underscore, non trattino)
- **NODE_CLASS_MAPPINGS**: deve essere definito (anche vuoto) per ComfyUI
- **Relativi imports**: `from . import auth` — funziona perché la dir è il package
- **aiohttp**: già incluso in ComfyUI, nessuna dipendenza aggiuntiva
- **Auth WS**: il WebSocket `/nodefluxy/events/{id}` usa query param `?key=` (non header)

## API endpoints

| Endpoint | Auth | Descrizione |
|---|---|---|
| GET `/nodefluxy/ping` | no | health check |
| GET `/nodefluxy/key` | solo localhost | mostra API key |
| POST `/nodefluxy/execute` | sì | invia workflow JSON, restituisce prompt_id |
| GET `/nodefluxy/status/{id}` | sì | stato + progress (0.0–1.0) |
| GET `/nodefluxy/outputs/{id}` | sì | URL immagini output |
| POST `/nodefluxy/cancel` | sì | interrompe esecuzione corrente |
| POST `/nodefluxy/upload` | sì | carica immagine input (multipart) |
| WS `/nodefluxy/events/{id}` | via ?key= | stream eventi real-time |

## Stato corrente (2026-06-13)

- **Versione**: v1.0.0
- **Commit**: `4fa17f5` — initial release
- **GitHub**: https://github.com/ObiriecLabs/nodefluxy-bridge (PUBBLICO)
- **Dipendenze**: nessuna (aiohttp già in ComfyUI)

### Prossimi step

1. Test end-to-end su ComfyUI reale
2. Aggiungere CORS configurabile (ora wildcard `*`)
3. Rate limiting per `/nodefluxy/execute`
