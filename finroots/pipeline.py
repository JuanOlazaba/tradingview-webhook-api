"""Procesos de la empresa: comité diario (un reel al día) y consejo semanal."""
from __future__ import annotations

import datetime as dt
import json
import os
import traceback
from pathlib import Path
from zoneinfo import ZoneInfo

from . import tiktok
from .company import ROOT, STATE, Meeting, load_config, load_episodes, save_episodes
from .episode import validate, script_text

EPISODES = ROOT / "episodes"
MINUTES = ROOT / "minutes"


def today(cfg) -> dt.date:
    return dt.datetime.now(ZoneInfo(cfg["brand"].get("timezone", "Europe/Madrid"))).date()


def _ep_dir(n: int) -> Path:
    return EPISODES / f"ep{n:03d}"


def build_caption(cfg: dict, copy: dict) -> str:
    tags = " ".join(h if h.startswith("#") else "#" + h for h in copy.get("hashtags", []))
    return f"{copy['caption'].strip()}\n\n{cfg['brand']['disclaimer']}\n\n{tags}".strip()


# ---------------------------------------------------------------- comité diario

CURRICULUM = ROOT / "curriculum.md"


def lessons() -> list[tuple[str, str]]:
    import re
    return re.findall(r"^- \[(\w+)\] (.+)$", CURRICULUM.read_text(encoding="utf-8"), re.M)


def next_lesson() -> tuple[str, str]:
    done = {e.get("lesson") for e in load_episodes()} | {x for e in load_episodes() for x in e.get("lessons", [])}
    for lid, title in lessons():
        if lid not in done:
            return lid, title
    return lessons()[-1]


def write_episode(m: Meeting, number: int, prev: dict | None) -> dict:
    cfg = m.cfg
    lid, ltitle = next_lesson()
    recent, metaphors = [], []
    for k in range(max(1, number - 10), number):
        f = _ep_dir(k) / "episode.json"
        if f.exists():
            e = json.loads(f.read_text(encoding="utf-8"))
            recent.append(f"ep. {k}: {e.get('title')} — {e.get('core_idea')}")
            metaphors.append(", ".join(sorted({sc["type"] for sc in e.get("scenes", [])})))
    m.note("operations", f"Episodio {number}. LECCIÓN DEL TEMARIO QUE TOCA (obligatoria): [{lid}] {ltitle}.\n"
                         "Episodios recientes (no repetir sus ideas, historias ni metáforas):\n- " + "\n- ".join(recent))
    m.say("ideas", f"""Propón 3 enfoques MUY distintos e innovadores para enseñar la lección [{lid}] {ltitle}.
Cada enfoque: una historia o situación original (puede ser un personaje de la biblia o uno nuevo), una metáfora visual
nueva que no se haya usado antes en el canal, y 2–3 ilustraciones propias concretas (qué se dibuja y cómo se anima).
Nada de repetir cajones, huchas, bolas de nieve o las mismas cartas: inventa. Que sea memorable y fácil de entender.
Cifras ilustrativas con el cálculo hecho y comprobado. Formato JSON:
{{"proposals":[{{"lesson":"{lid}","angle":"","story":"","visual_metaphor":"","illustrations":["descripción del dibujo y su animación"],
"figures":"cifras con cálculo","hook":"gancho de 6–14 palabras","question":"pregunta con A/B/C","why_it_hooks":""}}]}}""",
          want_json=True)
    m.say("marketing", "Evalúa los 3 enfoques para TikTok: gancho, originalidad visual, retención, comentarios. "
                       "Puntúa de 1 a 10 y mejora el gancho del mejor. Máx. 150 palabras.")
    m.say("product", "Evalúa claridad didáctica del enfoque para principiantes y riesgo de errores (cifras, dibujos difíciles). "
                     "Máx. 120 palabras.")
    m.say("ceo", f"""Decide. Elige o combina un enfoque y cierra la ficha final en JSON:
{{"chosen":0,"why":"","ficha":{{"lesson":"{lid}","angle":"","story":"","visual_metaphor":"","illustrations":[],
"figures":"","hook":"","question":"","teaser_next":""}},"notes_for_studio":""}}""", want_json=True)

    task = f"""Escribe el episodio {number} completo según la ficha del CEO, en el JSON del motor:
{{"number":{number},"lesson":"{lid}","slug":"","title":"","topic":"{ltitle}","core_idea":"","series":"","characters":[],
"keywords":["4-6 raíces de palabras clave para resaltar en azul en los subtítulos, en minúscula"],
"scenes":[{{"type":"<objeto del catálogo>","chapter":"// 01 · el problema","sfx":"<efecto>","voice":"<frase hablada>","params":{{...}}}}]}}
Reglas: 12–14 escenas, 150–200 palabras de voz en total. La primera escena es el gancho de 3–5 s (chapter vacío,
6–14 palabras). Al menos 3 escenas 'illustration' con dibujos SVG propios de esta historia (estilo de marca, animados).
Textos en pantalla CORTOS (display: máx. 3 líneas de 1–3 palabras). Números siempre como número en params (sin texto).
Colores solo de marca ('co','bl','am' o hex de marca). La penúltima es options; la última es logo (params.next = adelanto).
Haz bien las cuentas: lo que se dice y lo que se ve debe coincidir exactamente.
Usa sobre todo 'art' (biblioteca de ilustraciones profesionales) y añade 'illustration' propia solo si la biblioteca
no tiene lo que necesitas.
EPISODIO DE REFERENCIA (nivel de calidad exigido; copia su estructura y su cuidado, NO su historia):
{(ROOT / 'episodes' / 'ep008' / 'episode.json').read_text(encoding='utf-8')[:7000]}"""
    ep = m.say("studio", task, want_json=True)
    for rnd in range(cfg["pipeline"].get("max_revisions", 2) + 1):
        ep["number"] = number
        ep["lesson"] = lid
        errs = validate(ep)
        if errs:
            m.note("it", "Validación automática del motor: el JSON NO es renderizable.\n- " + "\n- ".join(errs))
            if rnd == cfg["pipeline"].get("max_revisions", 2):
                raise RuntimeError("El episodio no pasa la validación técnica: " + "; ".join(errs))
            ep = m.say("studio", "Corrige los errores de validación de IT y devuelve el episodio completo.", want_json=True)
            continue
        m.note("it", "Validación automática del motor: OK, el episodio es renderizable.")
        break
    ep = review_and_fix(m, ep, number, "Revisión de Compliance")
    from .qa import gate
    before = json.dumps(ep, sort_keys=True, ensure_ascii=False)
    ep = gate(m, ep, number, _ep_dir(number) / "_qa")
    ep["lesson"] = lid
    if json.dumps(ep, sort_keys=True, ensure_ascii=False) != before:  # solo si Producto pidió cambios
        ep = review_and_fix(m, ep, number, "Revisión final de Compliance tras el control de calidad")
    ep["qa_ok"] = True
    return ep


def review_and_fix(m: Meeting, ep: dict, number: int, label: str) -> dict:
    """Compliance revisa; si pide cambios, el Estudio los aplica y se vuelve a revisar."""
    rounds = m.cfg["pipeline"].get("max_revisions", 2)
    for rnd in range(rounds + 1):
        review = m.say("compliance", f"""{label} del episodio {number}:
{script_text(ep)}
Comprueba también las cifras y notas de los params:
{json.dumps([s.get('params', {}) for s in ep['scenes']], ensure_ascii=False)[:6000]}
Devuelve JSON {{"approved":true|false,"issues":[{{"escena":"","problema":"","cambio":""}}]}}""", want_json=True)
        if review.get("approved"):
            return ep
        if rnd == rounds:
            raise RuntimeError("Compliance no aprueba el episodio tras las revisiones: "
                               + json.dumps(review.get("issues", []), ensure_ascii=False)[:1500])
        fixed = m.say("studio", "Aplica TODOS los cambios de Compliance al episodio y devuélvelo completo en el mismo "
                                f"formato JSON. Episodio actual:\n{json.dumps(ep, ensure_ascii=False)}", want_json=True)
        fixed["number"] = number
        errs = validate(fixed)
        if errs:
            m.note("it", "Validación tras la corrección: " + "; ".join(errs))
            fixed = m.say("studio", "Corrige estos errores de validación y devuelve el episodio completo: " + "; ".join(errs),
                          want_json=True)
            fixed["number"] = number
            if validate(fixed):
                raise RuntimeError("La corrección del Estudio no pasa la validación técnica")
        ep = fixed
    return ep


def daily(publish: bool = True, render: bool = True) -> dict:
    from . import ledger, limits, llm, owner
    llm.PRIORITY = True
    handle_owner_decisions()
    cfg = load_config()
    date = today(cfg)
    eps = load_episodes()
    pending = next((e for e in eps if e.get("status") in ("ready", "rendered")), None)
    number = pending["number"] if pending else max(e["number"] for e in eps) + 1
    prev = next((e for e in reversed(eps) if e["number"] == number - 1), None)
    d = _ep_dir(number)
    d.mkdir(parents=True, exist_ok=True)
    m = Meeting(f"Comité diario de contenido · {date.isoformat()} · Episodio {number}", cfg)
    result = {"date": date.isoformat(), "episode": number}
    try:
        if (d / "episode.json").exists():
            ep = json.loads((d / "episode.json").read_text(encoding="utf-8"))
            m.note("operations", f"El episodio {number} ya estaba escrito en el colchón; pasa directo a revisión.")
            errs = validate(ep)
            if errs:
                raise RuntimeError("Episodio del colchón inválido: " + "; ".join(errs))
            ready_entry = next((e for e in eps if e["number"] == number), {})
            if not ep.get("qa_ok") and (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
                from .qa import gate
                ep = gate(m, ep, number, d / "_qa")
                ep["qa_ok"] = True
                (d / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=1), encoding="utf-8")
            if ready_entry.get("compliance_ok"):
                m.note("compliance", "Episodio ya aprobado por Compliance cuando se escribió para el colchón.")
            elif os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
                ep = review_and_fix(m, ep, number, "Revisión final antes de publicar")
                (d / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=1), encoding="utf-8")
        else:
            ep = write_episode(m, number, prev)
            (d / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=1), encoding="utf-8")

        if (d / "copy.json").exists():
            copy = json.loads((d / "copy.json").read_text(encoding="utf-8"))
        else:
            copy = m.say("marketing", f"""Escribe el copy del episodio {number} ("{ep['title']}") en JSON:
{{"caption":"1–3 frases, con la pregunta A/B/C, sin el aviso legal (se añade solo)","hashtags":["4–6"],
"hook_variants":["variante A","variante B"],"cover_text":"máx 5 palabras","post_time":"HH:MM Europe/Madrid"}}""",
                         want_json=True)
            (d / "copy.json").write_text(json.dumps(copy, ensure_ascii=False, indent=1), encoding="utf-8")
        caption = build_caption(cfg, copy)
        (d / "caption.txt").write_text(caption, encoding="utf-8")
        (d / "script.txt").write_text(script_text(ep), encoding="utf-8")

        entry = next((e for e in eps if e["number"] == number), None)
        if not entry:
            entry = {"number": number}
            eps.append(entry)
        entry.update({"lesson": ep.get("lesson"), "slug": ep["slug"], "title": ep["title"], "topic": ep["topic"], "core_idea": ep["core_idea"],
                      "characters": ep.get("characters", []), "objects": sorted({s["type"] for s in ep["scenes"]}),
                      "question": next((" / ".join(s["params"].get("options", [])) for s in ep["scenes"] if s["type"] == "options"), ""),
                      "status": entry.get("status") if entry.get("status") in ("rendered",) else "ready"})
        save_episodes(eps)

        if render and entry.get("status") == "rendered" and (d / "video.mp4").exists():
            m.note("it", "El vídeo ya estaba renderizado (publicación pendiente de un intento anterior).")
            result["video"] = str(d / "video.mp4")
        elif render:
            from .qa import final_check, gate
            from .render import render_episode
            have_ai = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
            for attempt in range(4):
                r = render_episode(ep, d, cfg)
                if not have_ai:
                    break
                tl = json.loads((d / "timeline.json").read_text())
                verdict = final_check(m, ep, number, d / "video.mp4", tl, d / "_qa" / f"final{attempt}")
                if verdict.get("approved"):
                    m.note("product", f"Vídeo final revisado fotograma a fotograma: cero errores (intento {attempt + 1}).")
                    break
                if attempt == 3:
                    entry["status"] = "blocked"
                    save_episodes(eps)
                    raise RuntimeError("Producto no aprueba el vídeo final tras 4 intentos; no se envía a TikTok")
                ep = m.say("studio", "Producto ha encontrado errores en el VÍDEO FINAL. Arregla TODOS y devuelve el episodio "
                                     f"completo en el mismo formato JSON. Episodio actual:\n{json.dumps(ep, ensure_ascii=False)}",
                           want_json=True)
                ep["number"] = number
                ep = gate(m, ep, number, d / "_qa" / f"refix{attempt}")
                (d / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=1), encoding="utf-8")
            result.update(r)
            entry["status"] = "rendered"
            entry["duration"] = r["duration"]
            save_episodes(eps)
            m.note("it", f"Render OK: {r['duration']:.1f} s, voz: {'sí' if r['has_voice'] else 'NO (revisar TTS)'}.")

        pub_cfg = cfg["publishing"]
        if publish and render:
            if tiktok.have_credentials():
                res = tiktok.publish(d / "video.mp4", caption, pub_cfg)
                entry.update({"status": "published" if res["status"] == "PUBLISH_COMPLETE" else "sent_to_inbox",
                              "published_at": dt.datetime.utcnow().isoformat() + "Z", "tiktok": res})
                save_episodes(eps)
                m.note("it", f"TikTok: {res['status']} (modo {res['mode']}, publish_id {res['publish_id']}).")
                result["tiktok"] = res
            elif pub_cfg.get("dry_run_without_tokens", True):
                owner.request("Conectar la cuenta de TikTok @finroots",
                              "Para publicar solos necesitamos tu permiso en TikTok. Sigue `finroots/CONECTAR_TIKTOK.md` "
                              "(unos 15 minutos). Mientras tanto dejamos cada vídeo en los artefactos de GitHub para que "
                              "lo subas a mano.", by="IT")
                entry["status"] = "awaiting_manual_upload"
                save_episodes(eps)
                m.note("it", "Sin credenciales de TikTok: el vídeo queda listo en los artefactos de GitHub para subirlo a mano.")
            else:
                raise RuntimeError("Faltan credenciales de TikTok")
        result["ok"] = True
        (STATE / "last_daily.json").write_text(json.dumps({"date": date.isoformat(), "episode": number}))
    except limits.LimitReached as e:
        m.note("operations", f"PAUSA por límite ({e}). El episodio {number} queda guardado en su estado actual "
                             "y se retoma automáticamente cuando se reinicie el límite.")
        result.update(ok=False, paused=True, error=str(e))
    except Exception as e:  # noqa: BLE001
        m.note("operations", f"INCIDENCIA: {e}\n```\n{traceback.format_exc()[-1500:]}\n```")
        result.update(ok=False, error=str(e))
    finally:
        llm.PRIORITY = False
        if len(m.log) > 2 and not result.get("paused") and (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            try:
                m.say("operations", "Cierra el acta: decisiones, estado del episodio, incidencias y próximos pasos "
                                    "(con responsable). Máx. 120 palabras.")
            except Exception as e:  # noqa: BLE001
                m.note("operations", f"(no se pudo cerrar el acta con IA: {e})")
        MINUTES.mkdir(exist_ok=True)
        (MINUTES / f"{date.isoformat()}-ep{number:03d}.md").write_text(m.minutes(), encoding="utf-8")
        ledger.log("publicación" if result.get("ok") else ("pausa" if result.get("paused") else "incidencia"),
                   f"Ep. {number}: " + (f"{entry_status(number)}" if result.get("ok") else result.get("error", "")[:300]))
        if not result.get("ok") and not result.get("paused"):
            owner.request(f"Incidencia en el episodio {number}",
                          f"El comité diario no pudo completar el episodio {number}:\n\n> {result.get('error', '')[:800]}\n\n"
                          "IT lo reintentará en la próxima ejecución. Responde solo si quieres dar instrucciones.", by="Operaciones")
        ledger.write_panel()
    return result


def entry_status(n: int) -> str:
    e = next((x for x in load_episodes() if x["number"] == n), {})
    return f"{e.get('title', '')} · estado: {e.get('status', '?')}"


# ---------------------------------------------------------------- consejo semanal

def board() -> dict:
    from . import ledger, limits
    flag = STATE / "board_pending"
    try:
        out = _board()
        if flag.exists():
            flag.unlink()
        return out
    except limits.LimitReached as e:
        flag.write_text(str(e))
        ledger.log("pausa", f"Consejo semanal aplazado por límite ({e}); se celebrará en cuanto se reinicie.")
        ledger.write_panel()
        return {"ok": True, "paused": True}


def _board() -> dict:
    from . import ledger
    handle_owner_decisions()
    cfg = load_config()
    date = today(cfg)
    kp = json.loads((STATE / "kpis.json").read_text())
    if tiktok.have_credentials():
        try:
            snap = tiktok.metrics()
            snap["date"] = date.isoformat()
            kp["history"].append(snap)
            (STATE / "kpis.json").write_text(json.dumps(kp, ensure_ascii=False, indent=1))
        except Exception as e:  # noqa: BLE001
            print(f"[board] métricas no disponibles: {e}")
    m = Meeting(f"Consejo de administración · semana del {date.isoformat()}", cfg)
    m.say("operations", "Prepara el informe semanal: episodios publicados esta semana, incidencias, métricas reales "
                        "(seguidores, visualizaciones, likes, comentarios, compartidos por vídeo; si no hay, dilo), "
                        "qué vídeos funcionaron mejor y peor y por qué. Viñetas.")
    m.say("marketing", "Análisis de crecimiento: qué ganchos y temas retienen más, qué cambiar la semana que viene. 3 propuestas medibles.")
    m.say("product", "Estado del embudo y monetización. Siguiente paso concreto para generar ingresos al dueño, con coste y plazo.")
    m.say("it", "Máximo 2 mejoras técnicas para la semana (calidad de vídeo/voz, publicación cruzada, fiabilidad) con coste y esfuerzo.")
    m.say("ceo", "Presenta al consejo tu plan para la semana que viene: prioridades (máx. 3), propuestas a votar y KPIs objetivo.")
    res = m.say("board", """Delibera (cada consejero con su voz), vota las propuestas y fija directivas. JSON:
{"deliberation":"texto con las 3 voces","votes":[{"proposal":"","result":"aprobada|rechazada","why":""}],
"directives":["directiva medible para la semana"],"vetoes":[""],"kpi_targets":{"followers":0,"avg_views":0},
"message_to_owner":"resumen para el dueño: qué ha pasado, qué se decide, qué necesitamos de él (si algo)"}""", want_json=True)
    directives = "\n".join(f"{i+1}. {d}" for i, d in enumerate(res.get("directives", [])))
    (STATE / "directives.md").write_text(
        f"# Directivas vigentes del consejo\n\n_Sesión del {date.isoformat()}_\n\n{directives}\n\n"
        f"## Vetos\n" + "\n".join(f"- {v}" for v in res.get("vetoes", []) if v) +
        f"\n\n## Objetivos\n{json.dumps(res.get('kpi_targets', {}), ensure_ascii=False)}\n", encoding="utf-8")
    MINUTES.mkdir(exist_ok=True)
    (MINUTES / f"{date.isoformat()}-consejo.md").write_text(m.minutes(), encoding="utf-8")
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / f"{date.isoformat()}-informe-al-dueño.md").write_text(
        f"# Informe al dueño · {date.isoformat()}\n\n{res.get('message_to_owner', '')}\n\n## Directivas\n{directives}\n",
        encoding="utf-8")
    ledger.log("consejo", "Sesión semanal: " + "; ".join(res.get("directives", []))[:300])
    ledger.write_panel()
    return {"ok": True, "date": date.isoformat()}


# ---------------------------------------------------------------- reuniones de mejora (3 por semana)

TOPICS = {
    "contenido": ("Contenido y colchón de episodios", ["ideas", "studio", "marketing"],
                  "Calidad de los últimos guiones, continuidad de la trama y próximos 7 episodios."),
    "crecimiento": ("Crecimiento en TikTok", ["marketing", "ideas", "product"],
                    "Ganchos, retención, hashtags, horarios, formatos de serie, respuesta a comentarios."),
    "monetizacion": ("Producto y monetización", ["product", "marketing", "compliance"],
                     "Embudo: lead magnet, newsletter, afiliados, producto propio. Siguiente paso para ingresar dinero."),
    "tecnologia": ("Calidad de vídeo y tecnología", ["it", "studio", "operations"],
                   "Voz, ritmo, nuevos objetos visuales, fiabilidad de la cadena, publicación cruzada."),
    "finanzas": ("Finanzas y costes", ["operations", "product", "it"],
                 "Costes de IA y servicios frente a resultados; previsión de ingresos; dónde gastar o ahorrar."),
    "riesgos": ("Riesgos y cumplimiento", ["compliance", "operations", "marketing"],
                "Revisión legal del contenido publicado, reputación, normas de TikTok, privacidad del dueño."),
}
ORDER = list(TOPICS)
CONFIG_WHITELIST = {"voice.edge_voice", "voice.edge_rate", "render.fps", "render.sfx"}
BUFFER_TARGET = 3


def _set_cfg(key: str, value) -> bool:
    """Cambia un valor de config.yaml conservando los comentarios del dueño."""
    import re
    import yaml
    path = ROOT / "config.yaml"
    text = path.read_text(encoding="utf-8")
    parts = key.split(".")
    val = yaml.safe_dump(value, allow_unicode=True).strip().removesuffix("...").strip()
    lines = text.split("\n")
    idx, indent = -1, -2
    for depth, k in enumerate(parts):
        pat = re.compile(r"^" + " " * (2 * depth) + re.escape(k) + r":(\s|$)")
        for i in range(idx + 1, len(lines)):
            if depth and lines[i].strip() and not lines[i].startswith(" " * (2 * depth)) and not lines[i].lstrip().startswith("#"):
                break
            if pat.match(lines[i]):
                idx = i
                break
        else:
            idx = -1
        if idx < 0:
            break
    if idx >= 0:
        line = lines[idx]
        comment = ""
        m = re.search(r"\s+#.*$", line)
        if m:
            comment = m.group(0)
        lines[idx] = " " * (2 * (len(parts) - 1)) + parts[-1] + ": " + val + comment
        path.write_text("\n".join(lines), encoding="utf-8")
    else:
        cfg = yaml.safe_load(text)
        node = cfg
        for k in parts[:-1]:
            node = node.setdefault(k, {})
        node[parts[-1]] = value
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    yaml.safe_load(path.read_text(encoding="utf-8"))
    return True


def apply_actions(actions: list[dict], source: str) -> list[str]:
    from . import ledger, owner
    done = []
    stamp = ledger.now()
    for a in actions or []:
        t = a.get("type")
        try:
            if t == "backlog" and a.get("item"):
                with open(STATE / "backlog.md", "a", encoding="utf-8") as f:
                    f.write(f"- [ ] {a['item']} _(añadido por {source}, {stamp[:10]})_\n")
                done.append(f"backlog: {a['item']}")
            elif t == "decision" and a.get("text"):
                with open(STATE / "ceo_decisions.md", "a", encoding="utf-8") as f:
                    f.write(f"- {stamp[:10]} · {a['text']}\n")
                done.append(f"decisión: {a['text']}")
            elif t == "bible" and a.get("text"):
                with open(ROOT / "bible.md", "a", encoding="utf-8") as f:
                    f.write(f"\n- ({stamp[:10]}) {a['text']}")
                done.append(f"biblia: {a['text'][:80]}")
            elif t == "config" and a.get("key"):
                key = a["key"]
                if key in CONFIG_WHITELIST or key.startswith("models.effort."):
                    _set_cfg(key, a.get("value"))
                    done.append(f"config {key} = {a.get('value')}")
                else:
                    owner.request(f"Cambiar configuración: {key} → {a.get('value')}",
                                  a.get("why", "Propuesto en reunión."), {"config": {key: a.get("value")}}, by=source)
                    done.append(f"petición al dueño: config {key}")
            elif t == "owner_request" and a.get("title"):
                r = owner.request(a["title"], a.get("body", ""), a.get("apply_on_yes"), by=source)
                done.append(f"petición al dueño: {r['title']}")
        except Exception as e:  # noqa: BLE001
            done.append(f"(acción fallida {t}: {e})")
    for d in done:
        ledger.log("acción", d, source=source)
    return done


def handle_owner_decisions():
    """Aplica lo que el dueño ha aprobado y registra sus respuestas."""
    from . import ledger, owner
    for r in owner.sync():
        if r["status"] == "approved":
            for k, v in (r.get("apply_on_yes") or {}).get("config", {}).items():
                _set_cfg(k, v)
            with open(STATE / "ceo_decisions.md", "a", encoding="utf-8") as f:
                f.write(f"- {ledger.now()[:10]} · APROBADO POR EL DUEÑO: {r['title']} ({r.get('answer', '')})\n")
        ledger.log("dueño", f"{r['status']}: {r['title']}" + (f" — {r.get('note')}" if r.get("note") else ""))


def fill_buffer(cfg: dict, max_new: int = 1) -> list[int]:
    """Escribe episodios por adelantado hasta tener un colchón de BUFFER_TARGET listos."""
    from . import ledger
    made = []
    for _ in range(max_new):
        eps = load_episodes()
        if sum(1 for e in eps if e.get("status") == "ready") >= BUFFER_TARGET:
            break
        n = max(e["number"] for e in eps) + 1
        m = Meeting(f"Estudio · episodio {n} para el colchón", cfg)
        try:
            ep = write_episode(m, n, eps[-1])
            d = _ep_dir(n)
            d.mkdir(parents=True, exist_ok=True)
            (d / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "script.txt").write_text(script_text(ep), encoding="utf-8")
            copy = m.say("marketing", f"""Escribe el copy del episodio {n} ("{ep['title']}") en JSON:
{{"caption":"1–3 frases, con la pregunta A/B/C, sin el aviso legal (se añade solo)","hashtags":["4–6"],
"hook_variants":["variante A","variante B"],"cover_text":"máx 5 palabras","post_time":"HH:MM Europe/Madrid"}}""",
                         want_json=True)
            (d / "copy.json").write_text(json.dumps(copy, ensure_ascii=False, indent=1), encoding="utf-8")
            eps.append({"compliance_ok": True, "number": n, "slug": ep["slug"], "title": ep["title"], "topic": ep["topic"],
                        "core_idea": ep["core_idea"], "characters": ep.get("characters", []),
                        "objects": sorted({s["type"] for s in ep["scenes"]}), "status": "ready"})
            save_episodes(eps)
            made.append(n)
            ledger.log("episodio", f"Ep. {n} escrito y aprobado por Compliance: {ep['title']}")
        except Exception as e:  # noqa: BLE001
            from .limits import LimitReached
            if isinstance(e, LimitReached):
                raise
            ledger.log("incidencia", f"No se pudo escribir el ep. {n}: {e}")
        finally:
            (MINUTES / f"{today(cfg).isoformat()}-ep{n:03d}-estudio.md").write_text(m.minutes(), encoding="utf-8")
    return made


DAILY_UTC = (15, 37)


def next_topic(advance: bool = True) -> str:
    rot = STATE / "rotation.json"
    i = json.loads(rot.read_text()).get("next", 0) if rot.exists() else 0
    if advance:
        rot.write_text(json.dumps({"next": (i + 1) % len(ORDER)}))
    return ORDER[i % len(ORDER)]  # hora del comité diario (coincide con finroots-daily.yml)


def catch_up() -> dict | None:
    """Si el episodio de hoy no salió (límite, fallo, minutos de GitHub agotados), lo retoma ahora."""
    cfg = load_config()
    last = STATE / "last_daily.json"
    done = json.loads(last.read_text()).get("date") if last.exists() else None
    now = dt.datetime.utcnow()
    if done == today(cfg).isoformat() or (now.hour, now.minute) < DAILY_UTC:
        return None
    from . import ledger
    ledger.log("reanudación", "El episodio de hoy estaba pendiente; el comité diario lo retoma ahora.")
    return daily()


def improve(topic: str | None = None) -> dict:
    from . import ledger, limits
    cfg = load_config()
    MINUTES.mkdir(exist_ok=True)
    handle_owner_decisions()
    p = limits.paused()
    if p:
        ledger.log("pausa", f"Reunión aplazada: {p['reason']} (hasta {p['until'][:16]} UTC).")
        limits.defer_topic(topic or next_topic())
        ledger.write_panel()
        return {"ok": True, "paused": True}
    caught = catch_up()
    if caught is not None and not caught.get("ok"):
        ledger.write_panel()
        return {"ok": True, "catch_up": caught}
    if (STATE / "board_pending").exists():
        return {"ok": True, "board": board()}
    if not topic:
        pending = limits.agenda()
        topic = pending[0] if pending else next_topic()
    title, roles, focus = TOPICS[topic]
    stamp = dt.datetime.utcnow().strftime("%Y-%m-%d-%H%M")
    m = Meeting(f"Reunión de mejora · {title} · {stamp} UTC", cfg)
    m.note("operations", f"Orden del día: {focus}\nRevisad lo publicado, las métricas, el backlog y las respuestas del dueño.")
    try:
        for r in roles:
            m.say(r, f"Aporta desde tu rol a: {focus} Sé concreto: qué cambiarías, por qué, cómo lo medimos. "
                     "Si algo requiere al dueño, dilo. Máx. 180 palabras.")
        res = m.say("ceo", """Cierra la reunión. Decide y convierte las ideas en acciones. JSON:
{"summary":"3 líneas","actions":[
 {"type":"decision","text":"decisión que aplicamos desde ya"},
 {"type":"backlog","item":"tarea concreta con responsable"},
 {"type":"bible","text":"nota de continuidad o personaje nuevo"},
 {"type":"config","key":"voice.edge_rate","value":"+8%","why":""},
 {"type":"owner_request","title":"","body":"qué pedimos, opción recomendada, coste, riesgo, qué pasa si dice no","apply_on_yes":{}}
]}
Solo acciones con valor real (0–5). No pidas al dueño lo que ya está pendiente.""", want_json=True)
        done = apply_actions(res.get("actions", []), f"CEO ({title})")
        m.note("operations", "Acciones ejecutadas:\n" + ("\n".join(f"- {d}" for d in done) or "- ninguna"))
        ledger.log("reunión", f"{title}: {res.get('summary', '')[:200]}", topic=topic)
        limits.done_topic(topic)
        made = fill_buffer(cfg, max_new=1)
        out = {"ok": True, "topic": topic, "actions": done, "buffer_new": made}
    except limits.LimitReached as e:
        limits.defer_topic(topic)
        m.note("operations", f"PAUSA por límite ({e}). La reunión de «{title}» se retomará en cuanto se reinicie.")
        out = {"ok": True, "paused": True, "topic": topic}
    except Exception as e:  # noqa: BLE001
        m.note("operations", f"INCIDENCIA: {e}")
        ledger.log("incidencia", f"Reunión {title}: {e}")
        out = {"ok": False, "topic": topic, "error": str(e)}
    finally:
        (MINUTES / f"{stamp}-mejora-{topic}.md").write_text(m.minutes(), encoding="utf-8")
        ledger.write_panel()
    return out
