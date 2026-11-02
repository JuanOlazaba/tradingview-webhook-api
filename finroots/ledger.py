"""Registro de todo lo que pasa (actividad y costes) y el panel de control del dueño (PANEL.md)."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .company import ROOT, STATE, load_episodes

ACTIVITY = STATE / "activity.jsonl"
COSTS = STATE / "costs.json"
PANEL = ROOT / "PANEL.md"

# $ por millón de tokens: entrada, salida, lectura de caché, escritura de caché
PRICES = {
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.20, 2.5),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def log(kind: str, summary: str, **extra):
    """Añade una línea al registro de actividad (nunca se borra)."""
    STATE.mkdir(exist_ok=True)
    with open(ACTIVITY, "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": now(), "kind": kind, "summary": summary, **extra}, ensure_ascii=False) + "\n")


def add_usage(model: str, role: str, usage) -> float:
    p = PRICES.get(model, PRICES["claude-opus-5-5"])
    inp = getattr(usage, "input_tokens", 0) or 0
    out = getattr(usage, "output_tokens", 0) or 0
    cr = getattr(usage, "cache_read_input_tokens", 0) or 0
    cw = getattr(usage, "cache_creation_input_tokens", 0) or 0
    usd = (inp * p[0] + out * p[1] + cr * p[2] + cw * p[3]) / 1e6
    data = json.loads(COSTS.read_text()) if COSTS.exists() else {"days": {}, "roles": {}}
    day = dt.date.today().isoformat()
    data["days"][day] = round(data["days"].get(day, 0) + usd, 4)
    data["roles"][role] = round(data["roles"].get(role, 0) + usd, 4)
    COSTS.write_text(json.dumps(data, indent=1))
    return usd


def _activity(n: int = 25) -> list[dict]:
    if not ACTIVITY.exists():
        return []
    lines = ACTIVITY.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(x) for x in lines[-n:]]


def write_panel():
    from . import owner

    eps = load_episodes()
    reqs = owner.load()
    pend = [r for r in reqs if r["status"] == "pending"]
    costs = json.loads(COSTS.read_text()) if COSTS.exists() else {"days": {}, "roles": {}}
    days = sorted(costs["days"].items())
    last7 = sum(v for _, v in days[-7:])
    total = sum(v for _, v in days)
    kp = json.loads((STATE / "kpis.json").read_text()).get("history", [])
    user = (kp[-1].get("user") if kp else None) or {}
    buffer = [e for e in eps if e.get("status") == "ready"]
    minutes = sorted((ROOT / "minutes").glob("*.md"), reverse=True)[:12]
    act = list(reversed(_activity(20)))
    status_es = {"ready": "en colchón", "rendered": "renderizado", "sent_to_inbox": "en tus borradores de TikTok",
                 "published": "publicado", "published_manually": "publicado a mano",
                 "awaiting_manual_upload": "listo para subir a mano", "blocked": "bloqueado"}

    from .limits import agenda, paused
    pz = paused()
    L = [f"# Panel de Finroots", f"_Actualizado: {now()} · se regenera en cada reunión_", ""]
    if pz:
        L += [f"> **En pausa:** {pz['reason']}. Se reanuda sola a partir de {pz['until'][:16].replace('T', ' ')} UTC"
              f" y retoma lo pendiente{(': ' + ', '.join(agenda())) if agenda() else ''}.", ""]
    L += ["## Necesita tu sí"]
    if pend:
        L += [f"- **{r['title']}** — {('[responder aquí](' + r['url'] + ')') if r.get('url') else 'ver state/owner_requests.json'}"
              f" · pedido por {r['by']} el {r['created']}" for r in pend]
    else:
        L += ["Nada pendiente. Los agentes siguen trabajando."]
    L += ["", "## Estado",
          f"- Episodios: {len(eps)} · en colchón (listos): {len(buffer)}"
          f"{' (' + ', '.join(str(e['number']) for e in buffer) + ')' if buffer else ''}",
          f"- TikTok: {user.get('follower_count', '—')} seguidores · {user.get('likes_count', '—')} me gusta · "
          f"{user.get('video_count', '—')} vídeos",
          f"- Coste de IA: hoy {costs['days'].get(dt.date.today().isoformat(), 0):.2f} $ · este mes "
          f"{sum(v for d, v in days if d.startswith(dt.date.today().strftime('%Y-%m'))):.2f} $ de 20 $ · total {total:.2f} $",
          "", "## Episodios", "| # | Título | Estado |", "|---|---|---|"]
    for e in reversed(eps[-15:]):
        L.append(f"| {e['number']} | [{e['title']}](episodes/ep{e['number']:03d}/script.txt) | {status_es.get(e.get('status'), e.get('status'))} |")
    L += ["", "## Últimas reuniones"] + [f"- [{m.stem}](minutes/{m.name})" for m in minutes]
    L += ["", "## Actividad reciente"] + [f"- `{a['t']}` **{a['kind']}** — {a['summary']}" for a in act]
    L += ["", "## Directivas del consejo", (STATE / "directives.md").read_text(encoding="utf-8").split("\n", 2)[-1].strip()]
    dec = STATE / "ceo_decisions.md"
    if dec.exists():
        L += ["", "## Decisiones recientes de dirección"] + dec.read_text(encoding="utf-8").strip().splitlines()[-12:]
    L += ["", "---", "Registro completo: [actas](minutes/) · [informes](reports/) · [actividad](state/activity.jsonl) · "
          "[costes](state/costs.json) · [peticiones](state/owner_requests.json)"]
    PANEL.write_text("\n".join(L) + "\n", encoding="utf-8")
