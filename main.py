from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

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
