from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

latest_alerts = {}

class TVAlert(BaseModel):
    ticker: str
    price: float
    timeframe: str | None = None
    message: str | None = None
    extra: dict | None = None

@app.post("/tradingview/webhook")
async def tradingview_webhook(alert: TVAlert):
    latest_alerts[alert.ticker.upper()] = {
        "ticker": alert.ticker.upper(),
        "price": alert.price,
        "timeframe": alert.timeframe,
        "message": alert.message,
        "extra": alert.extra,
        "received_at": datetime.utcnow().isoformat() + "Z",
    }
    return {"status": "ok"}

@app.get("/alerts")
async def get_alerts():
    return latest_alerts
