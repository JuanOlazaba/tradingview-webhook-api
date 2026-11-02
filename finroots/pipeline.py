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

def write_episode(m: Meeting, number: int, prev: dict | None) -> dict:
    cfg = m.cfg
    m.note("operations", f"Hoy toca el episodio {number}. Último publicado: "
                         f"{(prev or {}).get('title', 'ninguno')}. Objetivo: 1 reel de 55–75 s listo para publicar.")
    m.say("ideas", f"""Propón 3 fichas para el episodio {number} que continúen la trama de la biblia
(siguiente paso lógico tras el episodio anterior). Formato JSON:
{{"proposals":[{{"topic":"","core_idea":"una frase","character":"personaje y situación concreta",
"figures":"cifras ilustrativas con el cálculo","objects":["3+ objetos del catálogo, al menos 1 no usado en el ep. anterior"],
"hook":"primer fotograma","question":"pregunta con A/B/C","teaser_next":"pregunta que deja para el siguiente"}}]}}""",
          want_json=True)
    m.say("marketing", "Evalúa las 3 propuestas para TikTok (gancho, retención, comentarios, serie). Puntúa de 1 a 10 "
                       "y propone mejoras concretas del gancho. Máx. 150 palabras.")
    m.say("product", "Evalúa valor educativo y encaje con el embudo de monetización. ¿Lleva CTA hoy? ¿Cuál? Máx. 120 palabras.")
    decision = m.say("ceo", """Decide. Elige una propuesta (o combina) y cierra la ficha final del episodio en JSON:
{"chosen":0,"why":"","ficha":{"topic":"","core_idea":"","character":"","figures":"","objects":[],"hook":"",
"question":"","teaser_next":"","cta":""},"notes_for_studio":""}""", want_json=True)

    task = f"""Escribe el episodio {number} completo según la ficha del CEO, en el JSON del motor:
{{"number":{number},"slug":"","title":"","topic":"","core_idea":"","series":"","characters":[],
"keywords":["4-6 raíces de palabras clave para resaltar en azul en los subtítulos, en minúscula"],
"scenes":[{{"type":"<objeto del catálogo>","chapter":"// 01 · el problema","sfx":"<efecto>","voice":"<frase hablada>","params":{{...}}}}]}}
Reglas: 12–14 escenas, 150–200 palabras de voz en total, la primera escena es el gancho (chapter vacío),
la penúltima es options, la última es logo con la frase de marca (params.next = teaser del siguiente).
Haz bien las cuentas: lo que se dice y lo que se ve debe coincidir."""
    ep = m.say("studio", task, want_json=True)
    for rnd in range(cfg["pipeline"].get("max_revisions", 2) + 1):
        ep["number"] = number
        errs = validate(ep)
        if errs:
            m.note("it", "Validación automática del motor: el JSON NO es renderizable.\n- " + "\n- ".join(errs))
            if rnd == cfg["pipeline"].get("max_revisions", 2):
                raise RuntimeError("El episodio no pasa la validación técnica: " + "; ".join(errs))
            ep = m.say("studio", "Corrige los errores de validación de IT y devuelve el episodio completo.", want_json=True)
            continue
        m.note("it", "Validación automática del motor: OK, el episodio es renderizable.")
        review = m.say("compliance", f"""Revisa el guion del episodio {number}:
{script_text(ep)}
Comprueba también las cifras de los params. Devuelve JSON:
{{"approved":true|false,"issues":[{{"scene":1,"problem":"","fix":""}}],"math_check":"tus cálculos"}}""", want_json=True)
        if review.get("approved"):
            return ep
        if rnd == cfg["pipeline"].get("max_revisions", 2):
            raise RuntimeError("Compliance no aprueba el episodio tras las revisiones: "
                               + json.dumps(review.get("issues", []), ensure_ascii=False))
        ep = m.say("studio", "Aplica TODOS los cambios de Compliance y devuelve el episodio completo.", want_json=True)
    return ep


def daily(publish: bool = True, render: bool = True) -> dict:
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
            if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
                review = m.say("compliance", f"Revisión final antes de publicar:\n{script_text(ep)}\n"
                               'Devuelve JSON {"approved":true|false,"issues":[...]}', want_json=True)
                if not review.get("approved"):
                    raise RuntimeError("Compliance bloquea el episodio: " + json.dumps(review.get("issues"), ensure_ascii=False))
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
        entry.update({"slug": ep["slug"], "title": ep["title"], "topic": ep["topic"], "core_idea": ep["core_idea"],
                      "characters": ep.get("characters", []), "objects": sorted({s["type"] for s in ep["scenes"]}),
                      "question": next((" / ".join(s["params"].get("options", [])) for s in ep["scenes"] if s["type"] == "options"), ""),
                      "status": entry.get("status") if entry.get("status") in ("rendered",) else "ready"})
        save_episodes(eps)

        if render and entry.get("status") == "rendered" and (d / "video.mp4").exists():
            m.note("it", "El vídeo ya estaba renderizado (publicación pendiente de un intento anterior).")
            result["video"] = str(d / "video.mp4")
        elif render:
            from .render import render_episode
            r = render_episode(ep, d, cfg)
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
                entry["status"] = "awaiting_manual_upload"
                save_episodes(eps)
                m.note("it", "Sin credenciales de TikTok: el vídeo queda listo en los artefactos de GitHub para subirlo a mano.")
            else:
                raise RuntimeError("Faltan credenciales de TikTok")
        result["ok"] = True
    except Exception as e:  # noqa: BLE001
        m.note("operations", f"INCIDENCIA: {e}\n```\n{traceback.format_exc()[-1500:]}\n```")
        result.update(ok=False, error=str(e))
    finally:
        if len(m.log) > 2 and (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            try:
                m.say("operations", "Cierra el acta: decisiones, estado del episodio, incidencias y próximos pasos "
                                    "(con responsable). Máx. 120 palabras.")
            except Exception as e:  # noqa: BLE001
                m.note("operations", f"(no se pudo cerrar el acta con IA: {e})")
        MINUTES.mkdir(exist_ok=True)
        (MINUTES / f"{date.isoformat()}-ep{number:03d}.md").write_text(m.minutes(), encoding="utf-8")
    return result


# ---------------------------------------------------------------- consejo semanal

def board() -> dict:
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
    return {"ok": True, "date": date.isoformat()}
