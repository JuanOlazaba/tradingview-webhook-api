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


# ---------------------------------------------------------------------------
# Finroots · conexión de la cuenta de TikTok (OAuth) y páginas legales que
# TikTok exige al registrar la app. Variables en Render:
#   TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET
# Redirect URI a registrar en TikTok: https://<tu-servicio>.onrender.com/tiktok/callback
# ---------------------------------------------------------------------------
import os
from urllib.parse import urlencode

import requests
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

TIKTOK_SCOPES = "user.info.basic,user.info.stats,video.upload,video.publish,video.list"


def _redirect_uri(request: Request) -> str:
    return os.environ.get("TIKTOK_REDIRECT_URI") or str(request.url_for("tiktok_callback")).replace("http://", "https://")


@app.get("/tiktok/connect")
async def tiktok_connect(request: Request):
    q = {"client_key": os.environ["TIKTOK_CLIENT_KEY"], "scope": TIKTOK_SCOPES, "response_type": "code",
         "redirect_uri": _redirect_uri(request), "state": "finroots"}
    return RedirectResponse("https://www.tiktok.com/v2/auth/authorize/?" + urlencode(q))


@app.get("/tiktok/callback", name="tiktok_callback", response_class=HTMLResponse)
async def tiktok_callback(request: Request, code: str = "", error: str = ""):
    if error or not code:
        return HTMLResponse(f"<h1>TikTok no ha autorizado la app</h1><p>{error}</p>", status_code=400)
    r = requests.post("https://open.tiktokapis.com/v2/oauth/token/", timeout=30, data={
        "client_key": os.environ["TIKTOK_CLIENT_KEY"], "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
        "code": code, "grant_type": "authorization_code", "redirect_uri": _redirect_uri(request)})
    data = r.json()
    rt = data.get("refresh_token")
    if not rt:
        return HTMLResponse(f"<h1>Error al obtener el token</h1><pre>{data}</pre>", status_code=400)
    return HTMLResponse(
        "<h1>Cuenta de TikTok conectada</h1>"
        "<p>Copia este valor en GitHub → Settings → Secrets and variables → Actions → "
        "<b>TIKTOK_REFRESH_TOKEN</b>. No lo compartas con nadie. Caduca en 365 días.</p>"
        f"<textarea rows=4 cols=80 readonly>{rt}</textarea>"
        f"<p>Permisos concedidos: {data.get('scope')}</p>")


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return ("<h1>Finroots · Política de privacidad</h1><p>Finroots es un canal educativo de finanzas. "
            "Esta aplicación solo se usa para publicar vídeos en la cuenta propia de Finroots y leer sus "
            "estadísticas. No recoge ni almacena datos de otros usuarios.</p>")


@app.get("/terms", response_class=HTMLResponse)
async def terms():
    return ("<h1>Finroots · Términos</h1><p>Contenido educativo. No constituye asesoramiento financiero ni "
            "recomendación de inversión. La aplicación es de uso interno de Finroots.</p>")
