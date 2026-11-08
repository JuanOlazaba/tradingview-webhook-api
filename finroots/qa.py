"""Control de calidad de Producto: ningún vídeo sale con un error gráfico o matemático.

1. Comprobación automática del motor (window.qa): texto inválido (NaN), gráficas sin línea,
   textos cortados, escenas demasiado cargadas.
2. Revisión de Producto con las capturas de cada escena: errores gráficos que solo se ven a ojo
   (solapes, ilustraciones rotas, textos ilegibles) y recálculo de TODAS las cifras.
Si hay cualquier error, el Estudio corrige y se vuelve a revisar.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .episode import script_text, validate


def scan(ep: dict, workdir: Path) -> tuple[list[dict], list[Path]]:
    """Dibuja cada escena (sin voz) y devuelve (problemas automáticos, capturas)."""
    from playwright.sync_api import sync_playwright
    from .render import build_html, build_timeline

    workdir.mkdir(parents=True, exist_ok=True)
    tl, _ = build_timeline(ep, workdir, {"provider": "none"})
    html = workdir / "qa.html"
    html.write_text(build_html(ep, tl, None), encoding="utf-8")
    shots: list[Path] = []
    launch = {"executable_path": os.environ["FINROOTS_CHROMIUM"]} if os.environ.get("FINROOTS_CHROMIUM") else {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"], **launch)
        pg = b.new_page(viewport={"width": 360, "height": 640})
        pg.goto(html.resolve().as_uri() + "?render=1")
        pg.evaluate("window.ready")
        auto = [x for x in pg.evaluate("qa()") if x["issues"]]
        for i, s in enumerate(tl["scenes"]):
            pg.evaluate(f"seek({s['start'] + s['dur'] * 0.92:.3f})")
            f = workdir / f"qa_{i:02d}.jpg"
            pg.screenshot(path=str(f), type="jpeg", quality=72)
            shots.append(f)
        b.close()
    return auto, shots


def product_review(m, ep: dict, number: int, shots: list[Path]) -> dict:
    params = [{"escena": i + 1, "type": s["type"], "voz": s["voice"],
               "params": {k: v for k, v in (s.get("params") or {}).items() if k != "svg"}}
              for i, s in enumerate(ep["scenes"])]
    return m.say("product", f"""CONTROL DE CALIDAD FINAL del episodio {number}. Tienes la captura de cada escena en orden
(escena 1 = primera imagen). Tu trabajo: que NO salga ni un solo error.
Revisa en cada captura: textos cortados o fuera de su sitio, solapes con los subtítulos, palabras partidas,
ilustraciones rotas o que no se entienden, gráficas que no cuadran con los números, escenas vacías o feas,
cifras en pantalla que no coinciden con la voz.
Recalcula TODAS las cifras (muestra los cálculos) y comprueba que la voz, la pantalla y las notas dicen lo mismo.
Datos de cada escena:
{json.dumps(params, ensure_ascii=False)[:9000]}
Devuelve JSON {{"approved":true|false,"math_check":"tus cálculos","issues":[{{"escena":1,"problema":"","arreglo":""}}]}}.
approved=true SOLO si no hay ningún problema.""", want_json=True, images=shots)


def gate(m, ep: dict, number: int, workdir: Path, rounds: int = 5) -> dict:
    """Bucle de calidad: Estudio corrige hasta que Producto aprueba. Devuelve el episodio aprobado."""
    for rnd in range(rounds + 1):
        auto, shots = scan(ep, workdir / f"qa{rnd}")
        if auto:
            m.note("it", "Control automático del motor: hay problemas visibles.\n" +
                   "\n".join(f"- escena {x['scene']} ({x['type']}): {'; '.join(x['issues'])}" for x in auto))
            feedback = "Arregla estos problemas visibles detectados por el control automático"
        else:
            rev = product_review(m, ep, number, shots)
            if rev.get("approved"):
                m.note("product", "Control de calidad superado: cero errores gráficos y matemáticos.")
                return ep
            feedback = "Producto ha rechazado el episodio. Arregla TODOS sus problemas"
        if rnd == rounds:
            raise RuntimeError("El episodio no supera el control de calidad de Producto tras las correcciones")
        fixed = m.say("studio", f"{feedback} y devuelve el episodio completo en el mismo formato JSON. "
                                f"Episodio actual:\n{json.dumps(ep, ensure_ascii=False)}", want_json=True)
        fixed["number"] = number
        errs = validate(fixed)
        if errs:
            fixed = m.say("studio", "Corrige estos errores de validación y devuelve el episodio completo: " + "; ".join(errs),
                          want_json=True)
            fixed["number"] = number
            if validate(fixed):
                continue
        ep = fixed
    return ep


def summary(ep: dict) -> str:
    return script_text(ep)


def video_frames(video: Path, timeline: dict, workdir: Path) -> list[Path]:
    """Fotogramas del VÍDEO FINAL (con la voz real): uno al final de cada escena."""
    import subprocess
    workdir.mkdir(parents=True, exist_ok=True)
    out = []
    for i, s in enumerate(timeline["scenes"]):
        f = workdir / f"v_{i:02d}.jpg"
        t = s["start"] + s["dur"] * 0.9
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                        "-vf", "scale=360:-1", "-q:v", "4", str(f)], check=True)
        out.append(f)
    return out


def final_check(m, ep: dict, number: int, video: Path, timeline: dict, workdir: Path) -> dict:
    """Revisión de Producto sobre el vídeo ya generado. Devuelve su veredicto."""
    shots = video_frames(video, timeline, workdir)
    return product_review(m, ep, number, shots)
