"""
Route /nodefluxy/* iniettate nel server aiohttp di ComfyUI.

Endpoints:
  GET  /nodefluxy/ping          → health check + versione
  GET  /nodefluxy/key           → mostra API key (solo da localhost)
  POST /nodefluxy/execute       → esegui workflow, restituisce prompt_id
  GET  /nodefluxy/status/{id}   → stato esecuzione
  GET  /nodefluxy/outputs/{id}  → immagini/video risultanti
  POST /nodefluxy/cancel        → interrompi esecuzione corrente
  POST /nodefluxy/upload        → carica immagine input
  WS   /nodefluxy/events/{id}   → stream eventi real-time
"""

import json
import asyncio
from aiohttp import web

from . import auth
from . import comfyui_client as cc

BRIDGE_VERSION = "1.0.0"

# prompt_id → {"status": str, "progress": float, "events": list}
_sessions: dict = {}

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-NODEFLUXY-Key",
}


def _json(data: dict, status: int = 200) -> web.Response:
    return web.Response(
        text=json.dumps(data),
        content_type="application/json",
        status=status,
        headers=CORS_HEADERS,
    )


def _require_auth(request) -> web.Response | None:
    if not auth.verify(request):
        return _json({"error": "Unauthorized — API key non valida"}, 401)
    return None


# ── Handlers ─────────────────────────────────────────────────────────────────

async def handle_options(request):
    return web.Response(headers=CORS_HEADERS)


async def handle_ping(request):
    return _json({
        "status": "ok",
        "bridge": BRIDGE_VERSION,
        "comfyui": "running",
    })


async def handle_key(request):
    # visibile solo da localhost per sicurezza
    host = request.host.split(":")[0]
    if host not in ("127.0.0.1", "localhost", "::1"):
        return _json({"error": "Forbidden"}, 403)
    return _json({"api_key": auth.get_key()})


async def handle_execute(request):
    err = _require_auth(request)
    if err:
        return err
    try:
        body = await request.json()
    except Exception:
        return _json({"error": "JSON non valido"}, 400)

    workflow = body.get("workflow")
    if not workflow:
        return _json({"error": "workflow mancante"}, 400)

    try:
        prompt_id = await cc.queue_prompt(workflow)
    except Exception as e:
        return _json({"error": f"ComfyUI non raggiungibile: {e}"}, 503)

    _sessions[prompt_id] = {"status": "queued", "progress": 0.0, "events": []}

    # avvia background task per raccogliere eventi
    asyncio.get_event_loop().create_task(_collect_events(prompt_id))

    return _json({"prompt_id": prompt_id, "status": "queued"})


async def handle_status(request):
    err = _require_auth(request)
    if err:
        return err
    prompt_id = request.match_info["prompt_id"]
    session = _sessions.get(prompt_id)
    if not session:
        # prova a leggere dalla history ComfyUI
        try:
            history = await cc.get_history(prompt_id)
            if prompt_id in history:
                return _json({"status": "complete", "progress": 1.0})
        except Exception:
            pass
        return _json({"error": "prompt_id non trovato"}, 404)
    return _json(session)


async def handle_outputs(request):
    err = _require_auth(request)
    if err:
        return err
    prompt_id = request.match_info["prompt_id"]
    try:
        history = await cc.get_history(prompt_id)
        outputs = cc.get_output_images(history, prompt_id)
        return _json({"prompt_id": prompt_id, "outputs": outputs})
    except Exception as e:
        return _json({"error": str(e)}, 500)


async def handle_cancel(request):
    err = _require_auth(request)
    if err:
        return err
    await cc.interrupt()
    return _json({"ok": True})


async def handle_upload(request):
    err = _require_auth(request)
    if err:
        return err
    try:
        reader = await request.multipart()
        field = await reader.next()
        filename = field.filename or "upload.png"
        image_bytes = await field.read()
        result = await cc.upload_image(filename, image_bytes)
        return _json(result)
    except Exception as e:
        return _json({"error": str(e)}, 500)


async def handle_events_ws(request):
    """WebSocket che streamma eventi real-time per un prompt_id."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    prompt_id = request.match_info["prompt_id"]

    # verifica API key via query param (WS non supporta header custom facilmente)
    key = request.query.get("key", "")
    if key != auth.get_key():
        await ws.send_json({"type": "error", "message": "Unauthorized"})
        await ws.close()
        return ws

    async def forward(event):
        if not ws.closed:
            await ws.send_json(event)

    await cc.stream_events(prompt_id, forward)
    await ws.close()
    return ws


# ── Background task ───────────────────────────────────────────────────────────

async def _collect_events(prompt_id: str):
    session = _sessions.get(prompt_id, {})
    session["status"] = "running"

    async def on_event(event):
        etype = event.get("type")
        if etype == "progress":
            val = event.get("value", 0)
            mx = event.get("max", 1)
            session["progress"] = round(val / mx, 3) if mx else 0
            session["status"] = "running"
        elif etype == "complete":
            session["status"] = "complete"
            session["progress"] = 1.0
        elif etype == "error":
            session["status"] = "error"
            session["error"] = event.get("message", "")
        session.setdefault("events", []).append(event)

    await cc.stream_events(prompt_id, on_event)


# ── Route registration ────────────────────────────────────────────────────────

def register_routes(routes):
    routes.options("/nodefluxy/{tail:.*}", handle_options)
    routes.get("/nodefluxy/ping", handle_ping)
    routes.get("/nodefluxy/key", handle_key)
    routes.post("/nodefluxy/execute", handle_execute)
    routes.get("/nodefluxy/status/{prompt_id}", handle_status)
    routes.get("/nodefluxy/outputs/{prompt_id}", handle_outputs)
    routes.post("/nodefluxy/cancel", handle_cancel)
    routes.post("/nodefluxy/upload", handle_upload)
    routes.get("/nodefluxy/events/{prompt_id}", handle_events_ws)


def load_config():
    auth.load_config()
