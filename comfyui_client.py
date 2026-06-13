"""
Client asincrono verso le API interne di ComfyUI (stessa porta 8188).
Il bridge parla con ComfyUI come se fosse un client esterno,
ma tutto gira nello stesso processo — zero latenza di rete.
"""

import json
import uuid
import asyncio
import aiohttp


COMFYUI_BASE = "http://127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())


async def queue_prompt(workflow: dict) -> str:
    """Invia il workflow alla coda ComfyUI. Restituisce prompt_id."""
    payload = {"prompt": workflow, "client_id": CLIENT_ID}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{COMFYUI_BASE}/prompt",
            json=payload,
        ) as resp:
            data = await resp.json()
            return data["prompt_id"]


async def get_history(prompt_id: str) -> dict:
    """Legge storia esecuzione per un prompt_id."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{COMFYUI_BASE}/history/{prompt_id}"
        ) as resp:
            return await resp.json()


async def get_queue() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COMFYUI_BASE}/queue") as resp:
            return await resp.json()


async def interrupt() -> None:
    async with aiohttp.ClientSession() as session:
        await session.post(f"{COMFYUI_BASE}/interrupt")


async def upload_image(filename: str, image_bytes: bytes) -> dict:
    """Carica un'immagine nella cartella input di ComfyUI."""
    data = aiohttp.FormData()
    data.add_field("image", image_bytes, filename=filename, content_type="image/png")
    data.add_field("overwrite", "true")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{COMFYUI_BASE}/upload/image", data=data
        ) as resp:
            return await resp.json()


async def stream_events(prompt_id: str, on_event):
    """
    Connette al WebSocket ComfyUI e forwarda eventi relativi a prompt_id.
    on_event(event_dict) viene chiamato per ogni evento rilevante.
    Termina quando il prompt è completato o in errore.
    """
    ws_url = f"ws://127.0.0.1:8188/ws?clientId={CLIENT_ID}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        event = json.loads(msg.data)
                        etype = event.get("type")
                        edata = event.get("data", {})

                        if etype == "progress":
                            await on_event({
                                "type": "progress",
                                "value": edata.get("value", 0),
                                "max": edata.get("max", 1),
                                "prompt_id": prompt_id,
                            })

                        elif etype == "executing":
                            if edata.get("prompt_id") == prompt_id:
                                node = edata.get("node")
                                if node is None:
                                    await on_event({"type": "complete", "prompt_id": prompt_id})
                                    return
                                await on_event({"type": "node", "node": node, "prompt_id": prompt_id})

                        elif etype == "execution_error":
                            if edata.get("prompt_id") == prompt_id:
                                await on_event({"type": "error", "message": edata.get("exception_message", ""), "prompt_id": prompt_id})
                                return

                    elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED):
                        break
    except Exception as e:
        await on_event({"type": "error", "message": str(e), "prompt_id": prompt_id})


def get_output_images(history: dict, prompt_id: str) -> list:
    """Estrae i path delle immagini output dalla history ComfyUI."""
    outputs = []
    prompt_history = history.get(prompt_id, {}).get("outputs", {})
    for node_id, node_output in prompt_history.items():
        for img in node_output.get("images", []):
            outputs.append({
                "filename": img["filename"],
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
                "url": f"{COMFYUI_BASE}/view?filename={img['filename']}&subfolder={img.get('subfolder','')}&type={img.get('type','output')}",
            })
        for vid in node_output.get("gifs", []):
            outputs.append({
                "filename": vid["filename"],
                "subfolder": vid.get("subfolder", ""),
                "type": "video",
                "url": f"{COMFYUI_BASE}/view?filename={vid['filename']}&subfolder={vid.get('subfolder','')}&type=output",
            })
    return outputs
