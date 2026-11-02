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


def _tiktok_missing() -> list[str]:
    return [k for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET") if not os.environ.get(k, "").strip()]


def _tiktok_error(msg: str, status: int = 400) -> HTMLResponse:
    return HTMLResponse("<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>"
                        "<body style='font-family:system-ui;max-width:640px;margin:40px auto;padding:0 16px'>"
                        f"<h1>Finroots · no se pudo conectar TikTok</h1><p>{msg}</p></body>", status_code=status)


@app.get("/tiktok/connect")
async def tiktok_connect(request: Request):
    missing = _tiktok_missing()
    if missing:
        return _tiktok_error("Faltan estas variables en Render → Environment: <b>" + ", ".join(missing) +
                             "</b>. Añádelas, pulsa Save Changes, espera a que ponga Deployed y vuelve a abrir este enlace.", 503)
    q = {"client_key": os.environ["TIKTOK_CLIENT_KEY"], "scope": TIKTOK_SCOPES, "response_type": "code",
         "redirect_uri": _redirect_uri(request), "state": "finroots"}
    return RedirectResponse("https://www.tiktok.com/v2/auth/authorize/?" + urlencode(q))


@app.get("/tiktok/callback", name="tiktok_callback", response_class=HTMLResponse)
async def tiktok_callback(request: Request, code: str = "", error: str = ""):
    if error or not code:
        return _tiktok_error(f"TikTok no ha autorizado la app ({error or 'sin código'}). Vuelve a intentarlo desde /tiktok/connect.")
    missing = _tiktok_missing()
    if missing:
        return _tiktok_error("Faltan estas variables en Render: <b>" + ", ".join(missing) + "</b>.", 503)
    r = requests.post("https://open.tiktokapis.com/v2/oauth/token/", timeout=30, data={
        "client_key": os.environ["TIKTOK_CLIENT_KEY"], "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
        "code": code, "grant_type": "authorization_code", "redirect_uri": _redirect_uri(request)})
    try:
        data = r.json()
    except ValueError:
        data = {"error": f"HTTP {r.status_code}"}
    rt = data.get("refresh_token")
    if not rt:
        return _tiktok_error("TikTok no devolvió el código. Respuesta: <code>" +
                             str(data.get("error_description") or data.get("error") or data)[:300] +
                             "</code>. Comprueba que el Client key y el Client secret son los del Sandbox y que el "
                             "Redirect URI es exactamente https://tradingview-webhook-api.onrender.com/tiktok/callback")
    return HTMLResponse(
        "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>"
        "<body style='font-family:system-ui;max-width:640px;margin:40px auto;padding:0 16px'>"
        "<h1>Finroots · cuenta de TikTok conectada</h1>"
        f"<p>Permisos concedidos: {data.get('scope')}</p>"
        "<p>Finroots ya puede enviar los vídeos del canal a la bandeja de TikTok y leer sus estadísticas.</p>"
        "<details style='margin-top:32px'><summary>Mostrar código para el dueño (no grabar)</summary>"
        "<p>Cópialo en GitHub → Settings → Secrets and variables → Actions → <b>TIKTOK_REFRESH_TOKEN</b>. "
        "No lo compartas. Caduca en 365 días.</p>"
        f"<textarea id=t rows=4 style='width:100%' readonly>{rt}</textarea>"
        "<button onclick=\"navigator.clipboard.writeText(document.getElementById('t').value);this.textContent='Copiado'\">Copiar</button>"
        "</details></body>")


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return ("<h1>Finroots · Política de privacidad</h1><p>Finroots es un canal educativo de finanzas. "
            "Esta aplicación solo se usa para publicar vídeos en la cuenta propia de Finroots y leer sus "
            "estadísticas. No recoge ni almacena datos de otros usuarios.</p>")


@app.get("/terms", response_class=HTMLResponse)
async def terms():
    return ("<h1>Finroots · Términos</h1><p>Contenido educativo. No constituye asesoramiento financiero ni "
            "recomendación de inversión. La aplicación es de uso interno de Finroots.</p>")


@app.get("/{filename}", include_in_schema=False)
async def tiktok_domain_verification(filename: str):
    """Fichero de verificación de dominio de TikTok (si el portal lo pide).
    Variables en Render: TIKTOK_VERIFY_FILENAME (p. ej. tiktokAbC123.txt) y TIKTOK_VERIFY_CONTENT."""
    from fastapi import HTTPException
    from fastapi.responses import PlainTextResponse
    import re
    if filename and filename == os.environ.get("TIKTOK_VERIFY_FILENAME"):
        return PlainTextResponse(os.environ.get("TIKTOK_VERIFY_CONTENT", ""))
    # Sin variables: TikTok nombra el fichero tiktok<código>.txt y su contenido es
    # tiktok-developers-site-verification=<código>, así que lo respondemos directamente.
    m = re.fullmatch(r"tiktok([A-Za-z0-9]{16,64})\.txt", filename or "")
    if m:
        return PlainTextResponse(f"tiktok-developers-site-verification={m.group(1)}")
    raise HTTPException(status_code=404)
