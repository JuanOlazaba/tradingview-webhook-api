from fastapi import FastAPI
from pydantic import BaseMode
from datetime import datetime

app = FastAPI(title="TradingView Gmail Bridge API")

# Aquí guardaremos la última alerta recibida
latest_alert = {}

class GmailAlert(BaseModel):
    alert: str
    message: str

@app.post("/alert")
async def receive_alert(data: GmailAlert):
    """
    Endpoint al que llama Google Apps Script.
    """
    global latest_alert
    latest_alert = {
        "alert": data.alert,
        "message": data.message,
        "received_at": datetime.utcnow().isoformat() + "Z",
    }
    print("ALERTA RECIBIDA ---->", latest_alert)
    return {"status": "ok"}

@app.get("/latest")
async def get_latest():
    """
    Endpoint que luego podrá leer tu GPT para ver la última alerta.
    """
    if not latest_alert:
        return {"status": "empty"}
    return latest_alert
