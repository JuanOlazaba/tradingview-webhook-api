"""Formato de episodio de Finroots: catálogo de objetos (componentes) y validación.

Un episodio es un JSON con escenas. Cada escena es un objeto reconocible dibujado
por el motor (render/template.html). Los agentes del estudio escriben este JSON;
IT lo valida aquí antes de renderizar.
"""
from __future__ import annotations

SFX = ["thud", "deflate", "print", "deal", "hit", "hit2", "rise", "ding", "cling", "tick", "whoosh", "coins", "pop", ""]

# Catálogo que leen los agentes. Mantener sincronizado con render/template.html.
COMPONENTS: dict[str, dict] = {
    "drawer": {"desc": "Cajón de madera donde cae un billete.", "params": {"amount": "int", "currency": "str?", "note": "str?"}},
    "bill_shrink": {"desc": "Contador de años + billete que encoge y pierde color (inflación).", "params": {"year_from": "int", "year_to": "int", "value_from": "num", "value_to": "num", "note": "str?"}},
    "receipt": {"desc": "Ticket que se imprime; precios que suben.", "params": {"header": "str?", "year_from": "int?", "year_to": "int?", "items": "[{label, from, to?}]", "total_from": "num?", "total_to": "num?", "note": "str?"}},
    "cards": {"desc": "2-3 cartas que se reparten con icono. Iconos: bag, piggy, chart, house, coin, clock, shield, card, building, rocket, scale, leaf.", "params": {"cards": "[{label, icon, lit?:bool}]", "question": "str?", "question_at": "num?", "note": "str?"}},
    "display": {"desc": "Tipografía gigante (Anton) para el momento fuerte; con píldoras opcionales. Máx 4 líneas cortas.", "params": {"lines": "[{text, color?:'co'|'bl', at?}]", "size": "'xl'|'m'|'s'", "pills": "[{text, dark?:bool}]?", "note": "str?"}},
    "phone": {"desc": "Móvil con la app del banco del personaje: saldo que cambia por pasos, movimientos, notificaciones y etiqueta lateral.", "params": {"name": "str", "label": "str?", "balance_steps": "[[segundo, saldo]]", "low": "num?", "rows": "[{label, amount(+/-), color(hex), at}]?", "notifications": "[{title, body, at}]?", "side": "{label, value, tone:''|'co'|'am'|'bl', at}?", "note": "str?"}},
    "levers": {"desc": "Título + 1-3 palancas/deslizadores que se mueven.", "params": {"title": "str?", "levers": "[{label, sub?, from?:0-100, to?:0-100}]", "note": "str?"}},
    "options": {"desc": "Pregunta final A/B/C (obligatoria en // tu turno). Incluye el aviso legal.", "params": {"options": "[str, str, str]", "disclaimer": "str?"}},
    "logo": {"desc": "Cierre: semilla que se dibuja + 'Finroots'. Siempre la última escena.", "params": {"next": "str? (teaser del próximo episodio)"}},
    "piggies": {"desc": "Dos huchas que se llenan a distinto ritmo, con nombre, etiqueta y contador.", "params": {"pigs": "[{name, tag?, sub?, fill:0-1, from?, to?, suffix?, at?, dur?}] (2)", "note": "str?"}},
    "chart": {"desc": "Gráfica de líneas que se dibuja con valores finales que cuentan.", "params": {"series": "[{name, points:[num], color?, end?, suffix?}] (1-2)", "x_labels": "[str]", "at": "num?", "dur": "num?", "note": "str?"}},
    "calendar": {"desc": "Calendario de sobremesa cuyo número salta (años, edades).", "params": {"label": "str", "from": "int", "to": "int", "sub": "str?", "at": "num?", "dur": "num?", "note": "str?"}},
    "snowball": {"desc": "Bola de nieve que rueda pendiente abajo y crece.", "params": {"start_label": "str?", "end_label": "str?", "dur": "num?", "note": "str?"}},
    "counter": {"desc": "Tarjeta con un número gigante que cuenta solo.", "params": {"label": "str", "from": "num?", "to": "num", "prefix": "str?", "suffix": "str? (por defecto ' €')", "decimals": "int?", "color": "''|'co'|'bl'|'am'", "sub": "str?", "note": "str?"}},
    "illustration": {"desc": "Ilustración PROPIA dibujada en SVG para este tema (lo que hace único cada vídeo). Estilo Finroots: formas planas, colores de marca (#15120e tinta, #e0522f coral, #2c4fb5 azul, #f2b84b ámbar, #f3ede2 crema, #ffffff), trazo 3–5, esquinas redondeadas, sombras suaves. viewBox='0 0 200 200'. Animaciones con clases: 'dw' (se dibuja el trazo; añade pathLength='1'), 'pop' (aparece con rebote), 'grow' (crece desde abajo), 'bob' (flota); retardo con style='--at:1.2s'. Máx. 6000 caracteres, sin texto largo dentro (máx. 3 palabras), sin imágenes externas.", "params": {"svg": "str (<svg ...>...</svg>)", "label": "str? (frase corta bajo la ilustración)", "note": "str?"}},
    "art": {"desc": "Ilustración PROFESIONAL de la biblioteca (preferente). Una grande con etiqueta y cifra, o 2–3 en fila para comparar. Biblioteca: ver lista de ilustraciones.", "params": {"asset": "nombre", "tag": "str? (chip arriba)", "value": "num? (cifra grande que cuenta)", "color": "''|'co'|'bl'", "label": "str? (frase corta abajo)", "items": "[{asset, label, value?, color?}] (2–3, en lugar de asset)", "note": "str?"}},
    "coins": {"desc": "Torres de monedas que se apilan (comparar cantidades).", "params": {"towers": "[{label, coins:1-14, value?, color?:''|'co'|'bl', suffix?}] (1-3)", "note": "str?"}},
}

REQUIRED_TOP = ["number", "slug", "title", "topic", "core_idea", "keywords", "scenes"]


def catalog_text() -> str:
    lines = ["CATÁLOGO DE OBJETOS (type → params). '?' = opcional. Tiempos 'at'/'dur' en segundos desde el inicio de la escena."]
    for k, v in COMPONENTS.items():
        ps = ", ".join(f"{p}: {t}" for p, t in v["params"].items())
        lines.append(f"- {k}: {v['desc']} | {ps}")
    from .assets import catalog_text as _assets
    lines.append("BIBLIOTECA DE ILUSTRACIONES para 'art' (nombre: qué representa):\n" + _assets())
    lines.append(f"Efectos de sonido válidos (campo sfx): {', '.join(s for s in SFX if s)}")
    return "\n".join(lines)


import re as _re

_SVG_BAD = _re.compile(r"<\s*(script|foreignObject|iframe|image|use|a)\b|\son\w+\s*=|javascript:|url\s*\(|href\s*=", _re.I)


def svg_problems(svg: str) -> list[str]:
    out = []
    if not svg.strip().startswith("<svg") or "</svg>" not in svg:
        out.append("la ilustración debe ser un único <svg>...</svg>")
    if len(svg) > 6500:
        out.append("la ilustración es demasiado grande (máx. 6000 caracteres)")
    if _SVG_BAD.search(svg):
        out.append("la ilustración contiene elementos no permitidos (script, enlaces, imágenes, url())")
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(svg)
    except Exception as e:  # noqa: BLE001
        out.append(f"el SVG no es válido: {e}")
    return out


def validate(ep: dict) -> list[str]:
    """Devuelve la lista de errores (vacía si el episodio es válido)."""
    errs: list[str] = []
    for k in REQUIRED_TOP:
        if k not in ep:
            errs.append(f"falta el campo '{k}'")
    scenes = ep.get("scenes") or []
    if not isinstance(scenes, list) or not (8 <= len(scenes) <= 16):
        errs.append(f"debe haber entre 8 y 16 escenas (hay {len(scenes) if isinstance(scenes, list) else 0})")
        return errs
    words = 0
    prev = None
    for i, s in enumerate(scenes):
        t = s.get("type")
        if t not in COMPONENTS:
            errs.append(f"escena {i+1}: type '{t}' no existe")
        if not str(s.get("voice", "")).strip():
            errs.append(f"escena {i+1}: falta 'voice'")
        if s.get("sfx", "") not in SFX:
            errs.append(f"escena {i+1}: sfx '{s.get('sfx')}' no válido")
        if t == prev and t not in ("display", "art", "illustration") and not s.get("allow_repeat"):
            errs.append(f"escena {i+1}: repite el mismo objeto '{t}' que la anterior")
        if t == "illustration":
            errs += [f"escena {i+1}: {e}" for e in svg_problems(str((s.get("params") or {}).get("svg", "")))]
        if not isinstance(s.get("params", {}), dict):
            errs.append(f"escena {i+1}: params debe ser un objeto")
        prev = t
        words += len(str(s.get("voice", "")).split())
    hook = str(scenes[0].get("voice", "")).strip().rstrip("»\"'” ")
    hw = len(hook.split())
    if not (5 <= hw <= 15):
        errs.append(f"el gancho (escena 1) debe durar 3–5 s: una pregunta o afirmación de 6–14 palabras; tiene {hw}")
    if scenes and scenes[-1].get("type") != "logo":
        errs.append("la última escena debe ser 'logo'")
    if not any(s.get("type") == "options" for s in scenes):
        errs.append("falta la escena 'options' (pregunta final A/B/C)")
    if scenes and "Finroots" not in scenes[-1].get("voice", ""):
        errs.append("la última escena debe decir: 'Esto ha sido Finroots. El dinero, desde la raíz.'")
    if not (110 <= words <= 215):
        errs.append(f"el guion tiene {words} palabras; para 55–75 s apunta a 140–200")
    if sum(1 for s in scenes if s.get("type") in ("illustration", "art")) < 3:
        errs.append("incluye al menos 3 escenas con ilustraciones ('art' de la biblioteca o 'illustration' propia)")
    for i, s in enumerate(scenes):
        if s.get("type") == "art":
            from .assets import ASSETS
            names = [s["params"].get("asset")] if not s.get("params", {}).get("items") else [x.get("asset") for x in s["params"]["items"]]
            bad = [n for n in names if n not in ASSETS]
            if bad:
                errs.append(f"escena {i+1}: ilustración desconocida {bad}; usa una de la biblioteca")
    blob = str(ep).lower()
    if "ilustrativ" not in blob:
        errs.append("las cifras deben marcarse como 'ilustrativo' en algún 'note'")
    return errs


def script_text(ep: dict) -> str:
    return "\n".join(f"[{i+1:02d}] {s.get('chapter','')}  {s['voice']}" for i, s in enumerate(ep["scenes"]))
