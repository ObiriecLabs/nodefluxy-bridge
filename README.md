# NODEFLUXY Bridge

Custom node ComfyUI che connette NODEFLUXY alla tua installazione locale.

## Cosa fa

Aggiunge endpoint `/nodefluxy/*` al server di ComfyUI (porta 8188).  
NODEFLUXY usa questi endpoint per:
- Inviare workflow generati direttamente in coda
- Monitorare il progresso in real-time via WebSocket
- Recuperare le immagini/video prodotti

## Installazione rapida

```bash
bash <(curl -s https://raw.githubusercontent.com/ObiriecLabs/nodefluxy-bridge/main/install.sh)
```

Oppure manuale:

```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/ObiriecLabs/nodefluxy-bridge
# riavvia ComfyUI
```

## Configurazione

Al primo avvio ComfyUI stampa nel log:

```
  ✦ NODEFLUXY Bridge attivo → /nodefluxy/* su porta 8188

  ✦ NODEFLUXY Bridge — API Key generata:
    a3f9e2b1c4d5...
    Copiala in NODEFLUXY → Impostazioni → Bridge API Key
```

Copia la chiave in NODEFLUXY → Impostazioni → **Bridge API Key**.

## API

| Endpoint | Metodo | Descrizione |
|---|---|---|
| `/nodefluxy/ping` | GET | Health check |
| `/nodefluxy/key` | GET | Mostra API key (solo localhost) |
| `/nodefluxy/execute` | POST | Esegui workflow |
| `/nodefluxy/status/{id}` | GET | Stato esecuzione |
| `/nodefluxy/outputs/{id}` | GET | Output (immagini/video) |
| `/nodefluxy/cancel` | POST | Interrompi esecuzione |
| `/nodefluxy/upload` | POST | Carica immagine input |
| `/nodefluxy/events/{id}` | WS | Stream eventi real-time |

Auth: header `X-NODEFLUXY-Key: <api_key>` su tutte le chiamate tranne `/ping`.

## Aggiornamento

```bash
cd /path/to/ComfyUI/custom_nodes/nodefluxy_bridge
git pull
# riavvia ComfyUI
```

## Requisiti

- ComfyUI (qualsiasi versione recente)
- Python 3.9+
- `aiohttp` (già incluso in ComfyUI)
