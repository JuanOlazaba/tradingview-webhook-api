"""Cliente de Claude para los agentes de Finroots."""
from __future__ import annotations

import json
import os
import re

import anthropic

_client: anthropic.Anthropic | None = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=4, timeout=600)
    return _client


def ask(system_blocks: list[dict], user: str, model: str, effort: str = "medium", max_tokens: int = 16000, role: str = "?") -> str:
    """Una llamada a Claude. `system_blocks` lleva primero el contexto estable (cacheado)."""
    kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        system=system_blocks,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": effort},
    )
    if os.environ.get("FINROOTS_NO_FALLBACK") != "1":
        kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    with client().beta.messages.stream(**kwargs) as stream:
        msg = stream.get_final_message()
    try:
        from .ledger import add_usage
        add_usage(model, role, msg.usage)
    except Exception as e:  # noqa: BLE001
        print(f"[llm] no se pudo registrar el coste: {e}")
    if msg.stop_reason == "refusal":
        cat = getattr(msg.stop_details, "category", None) if msg.stop_details else None
        raise RuntimeError(f"El modelo rechazó la petición (categoría: {cat})")
    if msg.stop_reason == "max_tokens":
        print("[llm] aviso: respuesta cortada por max_tokens")
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def extract_json(text: str):
    """Saca el primer bloque JSON de una respuesta (```json ...``` o {...})."""
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    cand = m.group(1) if m else text
    start = min([i for i in (cand.find("{"), cand.find("[")) if i >= 0], default=-1)
    if start < 0:
        raise ValueError("no hay JSON en la respuesta")
    dec = json.JSONDecoder()
    obj, _ = dec.raw_decode(cand[start:])
    return obj
