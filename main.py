from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

from jarvis_icons import get_icon

app = FastAPI(title="TradingView Webhook API")

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

@app.get("/jarvis/{name}.png", include_in_schema=False)
async def jarvis_icon(name: str):
    data = get_icon(f"{name}.png")
    if data is None:
        raise HTTPException(status_code=404)
    return Response(data, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

app.mount("/jarvis", StaticFiles(directory=JARVIS_DIR, html=True), name="jarvis")
