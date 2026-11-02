"""Límites: cuando se agota algo (cuota de la API, saldo, presupuesto diario) la empresa se pausa
sola, guarda dónde se quedó y lo retoma cuando el límite se reinicia. No es una incidencia.

- 429 (límite de peticiones): pausa hasta lo que diga `retry-after` (mín. 15 min).
- 529 / sobrecarga: pausa 30 min.
- Límite de gasto mensual de la cuenta: pausa hasta el día 1 del mes siguiente y avisa al dueño.
- Saldo agotado: pausa 6 h y pide al dueño que recargue (cuando recargue, se retoma solo).
- Presupuesto diario propio (config.yaml → budget.daily_usd): las reuniones paran hasta mañana;
  el episodio del día tiene prioridad y sigue.
"""
from __future__ import annotations

import datetime as dt
import json

from .company import STATE

PAUSE = STATE / "pause.json"
AGENDA = STATE / "agenda.json"


class LimitReached(RuntimeError):
    pass


def _now():
    return dt.datetime.now(dt.timezone.utc)


def paused() -> dict | None:
    if not PAUSE.exists():
        return None
    p = json.loads(PAUSE.read_text())
    if dt.datetime.fromisoformat(p["until"]) <= _now():
        PAUSE.unlink()
        from .ledger import log
        log("reanudación", f"Se reinició el límite ({p['reason']}); retomamos donde lo dejamos.")
        return None
    return p


def pause(reason: str, until: dt.datetime, notify_owner: str | None = None):
    from .ledger import log
    cur = paused()
    if cur and dt.datetime.fromisoformat(cur["until"]) >= until:
        return
    PAUSE.write_text(json.dumps({"reason": reason, "until": until.isoformat(), "since": _now().isoformat()}))
    log("pausa", f"{reason}. Retomamos a partir de {until.strftime('%Y-%m-%d %H:%M UTC')}.")
    if notify_owner:
        from . import owner
        owner.request(notify_owner, f"{reason}. La empresa está en pausa y se reanudará sola en cuanto se "
                      "resuelva. No se pierde nada: el trabajo queda guardado donde se quedó.", by="Operaciones")


def from_api_error(e: Exception) -> LimitReached | None:
    """Traduce un error de la API de Claude en una pausa, si es un límite."""
    import anthropic
    msg = str(e).lower()
    now = _now()
    if isinstance(e, anthropic.RateLimitError):
        try:
            secs = int(e.response.headers.get("retry-after", "900"))
        except Exception:  # noqa: BLE001
            secs = 900
        pause("Límite de peticiones de la API de Claude", now + dt.timedelta(seconds=max(900, secs)))
        return LimitReached("límite de peticiones")
    if isinstance(e, anthropic.APIStatusError) and e.status_code in (529, 503):
        pause("API de Claude sobrecargada", now + dt.timedelta(minutes=30))
        return LimitReached("API sobrecargada")
    if isinstance(e, anthropic.APIStatusError) and ("usage limit" in msg or "spend limit" in msg or "api usage limits" in msg):
        nxt = (now.replace(day=1, hour=0, minute=5) + dt.timedelta(days=32)).replace(day=1)
        pause("Se alcanzó el límite de gasto mensual de la cuenta de Claude", nxt,
              notify_owner="Límite de gasto mensual de Claude alcanzado (opcional: subirlo)")
        return LimitReached("límite mensual")
    if isinstance(e, anthropic.APIStatusError) and ("credit balance" in msg or "billing" in msg):
        pause("Saldo de la cuenta de Claude agotado", now + dt.timedelta(hours=6),
              notify_owner="Recargar saldo de la cuenta de Claude")
        return LimitReached("saldo agotado")
    return None


def check_budget(cfg: dict, priority: bool):
    p = paused()
    if p:
        raise LimitReached(f"en pausa: {p['reason']} (hasta {p['until'][:16]} UTC)")
    budget = cfg.get("budget") or {}
    costs = STATE / "costs.json"
    days = json.loads(costs.read_text())["days"] if costs.exists() else {}
    month = dt.date.today().strftime("%Y-%m")
    spent_month = sum(v for d, v in days.items() if d.startswith(month))
    mcap = budget.get("monthly_usd")
    if mcap and spent_month >= mcap:
        now = _now()
        nxt = (now.replace(day=1, hour=0, minute=5, second=0, microsecond=0) + dt.timedelta(days=32)).replace(day=1)
        pause(f"Presupuesto mensual de IA alcanzado ({spent_month:.2f} $ de {mcap} $)", nxt)
        raise LimitReached("presupuesto mensual")
    cap = budget.get("daily_usd")
    if not cap or priority:
        return
    spent = days.get(dt.date.today().isoformat(), 0)
    if spent >= cap:
        tomorrow = (_now() + dt.timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0)
        pause(f"Presupuesto diario de IA alcanzado ({spent:.2f} $ de {cap} $)", tomorrow)
        raise LimitReached("presupuesto diario")


# ---- agenda: temas de reunión que quedaron a medias ----

def agenda() -> list[str]:
    return json.loads(AGENDA.read_text()) if AGENDA.exists() else []


def defer_topic(topic: str):
    a = agenda()
    if topic not in a:
        a.append(topic)
    AGENDA.write_text(json.dumps(a))


def done_topic(topic: str):
    a = [t for t in agenda() if t != topic]
    AGENDA.write_text(json.dumps(a))
