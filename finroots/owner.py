"""Canal con el dueño: peticiones de aprobación como Issues de GitHub.

Cuando los agentes necesitan algo que no pueden hacer solos (dinero, accesos, cambios de
riesgo), abren un Issue con la etiqueta `decision-dueño`. GitHub avisa al dueño por email y
en la app. El dueño responde en el Issue:
  "sí" / "si" / "ok" / "aprobado"  → se aplica y se cierra
  "no" (+ motivo opcional)         → se descarta y se cierra
Cualquier otro comentario se pasa a los agentes como instrucción del dueño.
En local (sin GITHUB_TOKEN) las peticiones se guardan solo en state/owner_requests.json.
"""
from __future__ import annotations

import json
import os
import re
import time

import requests

from .company import STATE

LABEL = "decision-dueño"
REQS = STATE / "owner_requests.json"
YES = re.compile(r"^\s*(s[ií]|ok|okay|vale|aprobad[oa]|adelante|yes|go)\b", re.I)
NO = re.compile(r"^\s*(no|rechazad[oa]|denegad[oa])\b", re.I)


def _repo():
    return os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")


def _gh(method: str, path: str, **kw):
    repo, tok = _repo()
    r = requests.request(method, f"https://api.github.com/repos/{repo}{path}", timeout=30,
                         headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}, **kw)
    if r.status_code >= 400 and r.status_code != 422:
        raise RuntimeError(f"GitHub {method} {path}: {r.status_code} {r.text[:200]}")
    return r.json() if r.text else {}


def load() -> list[dict]:
    return json.loads(REQS.read_text(encoding="utf-8")) if REQS.exists() else []


def save(reqs: list[dict]):
    REQS.write_text(json.dumps(reqs, ensure_ascii=False, indent=1), encoding="utf-8")


def request(title: str, body: str, apply_on_yes: dict | None = None, by: str = "CEO") -> dict:
    """Abre (una sola vez) una petición al dueño."""
    reqs = load()
    for r in reqs:
        if r["title"].lower() == title.lower() and r["status"] == "pending":
            return r
    req = {"id": len(reqs) + 1, "title": title, "body": body, "by": by, "status": "pending",
           "apply_on_yes": apply_on_yes or {}, "created": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}
    _open_issue(req)
    reqs.append(req)
    save(reqs)
    return req


def _open_issue(req: dict):
    repo, tok = _repo()
    if not (repo and tok) or req.get("issue"):
        return
    try:
        _gh("POST", "/labels", json={"name": LABEL, "color": "e0522f", "description": "Necesita el sí del dueño"})
        issue = _gh("POST", "/issues", json={
            "title": f"[Finroots] {req['title']}", "labels": [LABEL],
            "body": f"{req['body']}\n\n---\n**Pide:** {req['by']}\n\nResponde en un comentario **sí** para aprobar o **no** "
                    f"para rechazar (puedes añadir el motivo o instrucciones). Los agentes lo leen al momento."})
        req["issue"] = issue.get("number")
        req["url"] = issue.get("html_url")
        req.pop("issue_error", None)
    except Exception as e:  # noqa: BLE001
        req["issue_error"] = str(e)


def sync() -> list[dict]:
    """Lee las respuestas del dueño en los Issues. Devuelve las decisiones nuevas."""
    reqs = load()
    repo, tok = _repo()
    if not (repo and tok):
        return []
    owner = repo.split("/")[0].lower()
    for r in reqs:
        if r["status"] == "pending" and not r.get("issue"):
            _open_issue(r)
    new = []
    for r in reqs:
        if r["status"] != "pending" or not r.get("issue"):
            continue
        try:
            comments = _gh("GET", f"/issues/{r['issue']}/comments")
        except Exception:  # noqa: BLE001
            continue
        for c in comments:
            if c["user"]["login"].lower() != owner and c.get("author_association") not in ("OWNER", "COLLABORATOR"):
                continue
            if c["id"] in r.get("seen", []):
                continue
            r.setdefault("seen", []).append(c["id"])
            text = c["body"].strip()
            if YES.match(text):
                r.update(status="approved", answer=text, answered=c["created_at"])
            elif NO.match(text):
                r.update(status="rejected", answer=text, answered=c["created_at"])
            else:
                r.setdefault("owner_notes", []).append(text)
                new.append({**r, "status": "note", "note": text})
                continue
            new.append(r)
            _gh("POST", f"/issues/{r['issue']}/comments", json={"body": (
                "Recibido. " + ("Aprobado: lo aplicamos ahora." if r["status"] == "approved" else "Rechazado: queda descartado.")
                + "\n\n---\n_Finroots · agentes_")})
            _gh("PATCH", f"/issues/{r['issue']}", json={"state": "closed"})
            break
    save(reqs)
    return new


def context_text() -> str:
    reqs = load()
    pend = [r for r in reqs if r["status"] == "pending"]
    done = [r for r in reqs if r["status"] in ("approved", "rejected")][-10:]
    notes = [(r["title"], n) for r in reqs for n in r.get("owner_notes", [])][-10:]
    out = ["Pendientes del sí del dueño (no las vuelvas a pedir; sigue trabajando en lo demás):"]
    out += [f"- #{r['id']} {r['title']}" for r in pend] or ["- ninguna"]
    out.append("Respuestas del dueño:")
    out += [f"- {r['title']}: {r['status'].upper()} — {r.get('answer', '')}" for r in done] or ["- ninguna todavía"]
    if notes:
        out.append("Instrucciones del dueño (prioridad máxima):")
        out += [f"- ({t}) {n}" for t, n in notes]
    return "\n".join(out)
