"""Morning meeting de Jarvis.

Cada mañana una rutina de Claude escribe el informe, lo cifra con JARVIS_KEY y lo
sube a la rama `jarvis-data` del repositorio (que es público: por eso va cifrado).
Este módulo lo descarga, lo descifra y genera el audio con una voz neuronal.
"""
import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import urllib.request
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger("jarvis")

DATA_URL = os.getenv(
    "JARVIS_DATA_URL",
    "https://raw.githubusercontent.com/JuanOlazaba/tradingview-webhook-api/jarvis-data/briefings/latest.enc",
)
VOICE = os.getenv("JARVIS_VOICE", "es-US-AlonsoNeural")
RATE = os.getenv("JARVIS_RATE", "+0%")
AUDIO_DIR = Path(os.getenv("JARVIS_AUDIO_DIR", "/tmp/jarvis_audio"))
CACHE_SECONDS = 120

_cache = {"at": 0.0, "briefing": None}
_audio_tasks = {}


def configured():
    return bool(os.getenv("JARVIS_KEY")) and bool(os.getenv("JARVIS_PIN"))


def check_pin(given):
    pin = os.getenv("JARVIS_PIN", "")
    return bool(pin) and bool(given) and hmac.compare_digest(given.strip().upper(), pin.upper())


def _download():
    req = urllib.request.Request(f"{DATA_URL}?t={int(time.time())}", headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.read()


def decrypt(blob, key):
    return json.loads(Fernet(key.encode()).decrypt(blob.strip()))


async def get_briefing(force=False):
    """Devuelve el último informe descifrado, o None si no hay."""
    if not force and time.time() - _cache["at"] < CACHE_SECONDS:
        return _cache["briefing"]
    key = os.getenv("JARVIS_KEY")
    if not key:
        return None
    try:
        blob = await asyncio.to_thread(_download)
        briefing = decrypt(blob, key)
        if briefing != _cache["briefing"]:
            # Informe nuevo: empezamos a preparar el audio en segundo plano
            asyncio.create_task(get_audio(briefing, wait=600))
        _cache["briefing"] = briefing
    except (InvalidToken, ValueError) as exc:
        log.warning("No se pudo descifrar el informe: %s", exc)
    except Exception as exc:  # red, 404 si todavía no hay informes, etc.
        log.warning("No se pudo descargar el informe: %s", exc)
    _cache["at"] = time.time()
    return _cache["briefing"]


def speech_text(briefing):
    """Texto que lee la voz: título y cada sección."""
    parts = [briefing.get("title", "")]
    for section in briefing.get("sections", []):
        parts.append(f"{section.get('title', '')}.")
        parts.append(section.get("text", ""))
    if briefing.get("closing"):
        parts.append(briefing["closing"])
    return "\n\n".join(p for p in parts if p and p.strip())


async def _render(text, path):
    import edge_tts

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(tmp))
    tmp.rename(path)
    return path


async def get_audio(briefing, wait=150):
    """Devuelve la ruta del MP3 (lo genera si hace falta) o None si falla."""
    text = speech_text(briefing)
    digest = hashlib.sha256(f"{VOICE}|{RATE}|{text}".encode()).hexdigest()[:20]
    path = AUDIO_DIR / f"{digest}.mp3"
    if path.exists():
        return path
    task = _audio_tasks.get(digest)
    if task is None or (task.done() and task.exception() is not None):
        task = asyncio.create_task(_render(text, path))
        _audio_tasks[digest] = task
    try:
        return await asyncio.wait_for(asyncio.shield(task), wait)
    except Exception as exc:
        log.warning("No se pudo generar el audio: %r", exc)
        return None


async def warm_up():
    """Al arrancar, descarga el último informe (y empieza a preparar su audio)."""
    await get_briefing(force=True)
