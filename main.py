import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

import jarvis_briefing
from jarvis_icons import get_icon


@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(jarvis_briefing.warm_up())
    yield
    task.cancel()


app = FastAPI(title="TradingView Webhook API", lifespan=lifespan)

# Aquí guardamos la última alerta recibida
last_alert = {}

class GmailAlert(BaseModel):
    alert: str      # Ej: "KOS"
    message: str    # Texto completo del email

@app.post("/alert")
async def receive_alert(info: GmailAlert):
    """
    Endpoint que llama Apps Script desde Gmail.
    """
    global last_alert
    last_alert = {
        "alert": info.alert,
        "message": info.message,
        "received_at": datetime.utcnow().isoformat() + "Z"
    }
    return last_alert

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/last_alert")
async def get_last_alert():
    """
    Endpoint de solo lectura para que el GPT consulte la última alerta.
    """
    if not last_alert:
        return {"has_alert": False}
    return {"has_alert": True, **last_alert}


# App móvil de Jarvis (PWA instalable): abre https://<tu-servicio>/jarvis/ en el teléfono
JARVIS_DIR = Path(__file__).parent / "jarvis"

@app.get("/jarvis", include_in_schema=False)
async def jarvis_redirect():
    return RedirectResponse("/jarvis/")

def _require_pin(pin):
    if not jarvis_briefing.configured():
        raise HTTPException(status_code=503, detail="Faltan JARVIS_KEY y JARVIS_PIN en Render")
    if not jarvis_briefing.check_pin(pin):
        raise HTTPException(status_code=401, detail="Código de acceso incorrecto")

@app.get("/briefing", include_in_schema=False)
async def get_briefing(key: str = "", x_jarvis_key: str = Header(default="")):
    """Último morning meeting (protegido con el código de acceso)."""
    _require_pin(x_jarvis_key or key)
    briefing = await jarvis_briefing.get_briefing()
    if not briefing:
        return {"has_briefing": False}
    return {"has_briefing": True, **briefing}

@app.get("/jarvis/briefing.mp3", include_in_schema=False)
async def get_briefing_audio(key: str = ""):
    _require_pin(key)
    briefing = await jarvis_briefing.get_briefing()
    if not briefing:
        raise HTTPException(status_code=404, detail="Todavía no hay informe")
    path = await jarvis_briefing.get_audio(briefing)
    if not path:
        raise HTTPException(status_code=503, detail="El audio no está disponible")
    return FileResponse(path, media_type="audio/mpeg", headers={"Cache-Control": "private, max-age=3600"})

@app.get("/jarvis/{name}.png", include_in_schema=False)
async def jarvis_icon(name: str):
    data = get_icon(f"{name}.png")
    if data is None:
        raise HTTPException(status_code=404)
    return Response(data, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

app.mount("/jarvis", StaticFiles(directory=JARVIS_DIR, html=True), name="jarvis")
