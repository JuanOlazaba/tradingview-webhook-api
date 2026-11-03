"""Renderiza un episodio: voz → línea de tiempo → HTML → fotogramas → MP4 9:16.

El motor (render/template.html) es determinista: `seek(t)` dibuja exactamente el
fotograma del segundo t, así que capturamos fotograma a fotograma con Chromium y
el vídeo sale perfectamente sincronizado con la voz.
"""
from __future__ import annotations

import base64
import re
import json
import os
import subprocess
import time
from pathlib import Path

from . import audio
from .episode import validate

HERE = Path(__file__).parent
TEMPLATE = HERE / "render" / "template.html"
FONTS = HERE / "render" / "fonts"


def _fonts_css() -> str:
    meta = json.loads((FONTS / "fonts.json").read_text())
    css = []
    for f in meta:
        data = base64.b64encode((FONTS / f["file"]).read_bytes()).decode()
        css.append(f"@font-face{{font-family:'{f['family']}';font-weight:{f['weight']};font-style:normal;font-display:block;"
                   f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{f['range']}}}")
    return "\n".join(css)


def build_timeline(ep: dict, workdir: Path, voice_cfg: dict) -> tuple[dict, list]:
    lead, tail, min_dur = 0.15, 0.35, 2.4
    t = 0.0
    scenes, files = [], []
    for i, s in enumerate(ep["scenes"]):
        f = workdir / f"voice_{i:02d}.mp3"
        dur, words = audio.synth_voice(s["voice"], f, voice_cfg)
        files.append(f if f.exists() and f.stat().st_size > 0 else None)
        sd = max(min_dur, float(s.get("min_t", 0)), lead + dur + tail)
        merged = []
        for w, wt in words:  # "57.430 €." se muestra junto: la unidad nunca va sola en el subtítulo
            if merged and (re.fullmatch(r"[€%$]+[.,;:!?…]*|pts\.?|€/\w+\.?", w) or not re.search(r"\w", w)):
                merged[-1] = (merged[-1][0] + " " + w, merged[-1][1])
            else:
                merged.append((w, wt))
        scenes.append({"start": round(t, 3), "dur": round(sd, 3), "lead": lead,
                       "words": [[w, round(t + lead + wt, 3)] for w, wt in merged]})
        t += sd
    return {"total": round(t, 3), "scenes": scenes}, files


def build_html(ep: dict, timeline: dict, audio_src: str | None = None) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    title = f"Finroots · Ep. {ep['number']} · {ep['title']}"
    return (html.replace("__TITLE__", title)
            .replace("__FONTS__", _fonts_css())
            .replace("__EPISODE__", json.dumps(ep, ensure_ascii=False))
            .replace("__TIMELINE__", json.dumps(timeline, ensure_ascii=False))
            .replace("__AUDIO__", json.dumps(audio_src)))


def capture(html_path: Path, total: float, out_mp4: Path, wav: Path, fps: int = 30, width: int = 1080):
    from playwright.sync_api import sync_playwright

    height = width * 16 // 9
    n = int(total * fps)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
        "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart", str(out_mp4)],
        stdin=subprocess.PIPE)
    launch = {}
    exe = os.environ.get("FINROOTS_CHROMIUM")
    if exe:
        launch["executable_path"] = exe
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--force-color-profile=srgb"], **launch)
        pg = b.new_page(viewport={"width": width // 2, "height": height // 2}, device_scale_factor=2)
        pg.goto(html_path.resolve().as_uri() + "?render=1")
        pg.evaluate("window.ready")
        for k in range(n):
            pg.evaluate(f"seek({k / fps:.4f})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=92, animations="allow", caret="hide"))
            if k and k % (fps * 10) == 0:
                print(f"  [render] {k}/{n} fotogramas ({time.time() - t0:.0f}s)")
        # Portada (primer fotograma con texto completo de la escena 1)
        pg.evaluate("seek(1.2)")
        pg.screenshot(path=str(out_mp4.with_name("cover.jpg")), type="jpeg", quality=90)
        b.close()
    ff.stdin.close()
    ff.wait()
    if ff.returncode:
        raise RuntimeError("ffmpeg falló al codificar el vídeo")
    print(f"  [render] {out_mp4.name} listo en {time.time() - t0:.0f}s")


def render_episode(ep: dict, outdir: Path, cfg: dict) -> dict:
    errs = validate(ep)
    if errs:
        raise ValueError("Episodio inválido:\n- " + "\n- ".join(errs))
    outdir.mkdir(parents=True, exist_ok=True)
    work = outdir / "_work"
    work.mkdir(exist_ok=True)
    rcfg = cfg.get("render", {})
    timeline, files = build_timeline(ep, work, cfg.get("voice", {}))
    wav = audio.build_mix(timeline, ep["scenes"], files, work / "mix.wav", fx_on=rcfg.get("sfx", True),
                          music_volume=float(rcfg.get("music_volume", 0.22)), music_duck=float(rcfg.get("music_duck", 0.45)),
                          music_variant=int(ep.get("number", 0)))
    has_voice = any(files)
    mp3 = outdir / "audio.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "160k", str(mp3)], check=True)
    # Vista previa interactiva (con la pista final si hay voz)
    (outdir / "reel.html").write_text(build_html(ep, timeline, "audio.mp3" if has_voice else None), encoding="utf-8")
    render_html = work / "render.html"
    render_html.write_text(build_html(ep, timeline, None), encoding="utf-8")
    (outdir / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
    mp4 = outdir / "video.mp4"
    capture(render_html, timeline["total"], mp4, wav, fps=rcfg.get("fps", 30), width=rcfg.get("width", 1080))
    return {"video": str(mp4), "duration": timeline["total"], "has_voice": has_voice}
