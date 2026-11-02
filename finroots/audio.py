"""Voz (TTS) y efectos de sonido sintetizados.

Proveedores de voz, en orden de calidad:
  - elevenlabs (si hay ELEVENLABS_API_KEY): voz más natural, de pago.
  - edge (gratis, voces neurales de Microsoft, p. ej. es-ES-AlvaroNeural).
  - none: sin voz (solo para pruebas); estima tiempos por número de palabras.
Cada proveedor devuelve la duración y los tiempos de cada palabra para el karaoke.
"""
from __future__ import annotations

import asyncio
import base64
import json
import math
import os
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100


def _duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def _estimate_words(text: str, dur: float) -> list[tuple[str, float]]:
    ws = text.split()
    total = sum(len(w) + 2 for w in ws) or 1
    t, out = 0.0, []
    for w in ws:
        out.append((w, t))
        t += dur * 0.95 * (len(w) + 2) / total
    return out


def _speakable(text: str) -> str:
    return text.replace("...", "…")


def _pct(v: str) -> int:
    return int(str(v).replace("%", "").replace("+", "") or 0)


def _prosody(sentence: str, i: int, base_rate: int) -> tuple[str, str, float]:
    """Entonación por frase para que la voz no suene plana: (rate, pitch, pausa_después)."""
    words = len(sentence.split())
    s = sentence.strip()
    if s.endswith("...") or s.endswith("…"):
        rate, pitch, pause = base_rate - 4, -4, 0.45
    elif s.endswith("?"):
        rate, pitch, pause = base_rate + 4, 14, 0.22
    elif s.endswith("!") or words <= 4:
        rate, pitch, pause = base_rate + 10, 8, 0.15
    else:
        rate, pitch, pause = base_rate + (3 if i % 2 else 0), (4 if i % 2 else 0), 0.12
    return f"{rate:+d}%", f"{pitch:+d}Hz", pause


def tts_edge(text: str, out: Path, voice: str, rate: str) -> tuple[float, list]:
    """Voz neural gratuita, frase a frase con entonación variada (voz más dinámica)."""
    import re
    import edge_tts

    # Corta por frases (no rompe cifras como 1.500): puntuación final seguida de espacio
    sentences = [x.strip() for x in re.split(r"(?<=[.?!…])\s+", text.strip()) if x.strip()] or [text]
    base = _pct(rate)
    tmpdir = out.parent / (out.stem + "_parts")
    tmpdir.mkdir(exist_ok=True)

    async def one(sentence: str, path: Path, r: str, p: str):
        com = edge_tts.Communicate(_speakable(sentence), voice, rate=r, pitch=p, boundary="WordBoundary")
        bounds = []
        with open(path, "wb") as f:
            async for ch in com.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    bounds.append((ch["text"], ch["offset"] / 1e7))
        return bounds

    words, parts, t = [], [], 0.0
    for i, sent in enumerate(sentences):
        r, p, pause = _prosody(sent, i, base)
        part = tmpdir / f"p{i:02d}.mp3"
        bounds = asyncio.run(one(sent, part, r, p))
        d = _duration(part)
        words += [(w, t + wt) for w, wt in _align(sent, bounds, d)]
        parts.append((part, pause))
        t += d + pause
    # Une las frases con sus pausas en un único audio
    inputs, filt = [], []
    for k, (part, pause) in enumerate(parts):
        inputs += ["-i", str(part)]
        filt.append(f"[{k}:a]aresample=44100,apad=pad_dur={pause}[a{k}]")
    filt.append("".join(f"[a{k}]" for k in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[out]", "-b:a", "160k", str(out)], check=True)
    for part, _ in parts:
        part.unlink(missing_ok=True)
    tmpdir.rmdir()
    return _duration(out), words


def _align(text: str, bounds: list, dur: float) -> list[tuple[str, float]]:
    """Asigna a cada palabra del guion el instante en que el TTS la pronuncia."""
    if not bounds:
        return _estimate_words(text, dur)
    src = _speakable(text)
    marks, pos = [], 0
    for btxt, bt in bounds:
        i = src.find(btxt, pos)
        if i >= 0:
            marks.append((i, bt))
            pos = i + len(btxt)
    if not marks:
        return _estimate_words(text, dur)
    out, pos = [], 0
    for w in src.split():
        i = src.find(w, pos)
        pos = i + len(w)
        t = marks[0][1]
        for ci, bt in marks:
            if ci <= i + len(w) - 1:
                t = bt
            else:
                break
        out.append((w.replace("…", "..."), t))
    mono, last = [], 0.0
    for w, t in out:
        last = max(last, t)
        mono.append((w, last))
    return mono


def tts_elevenlabs(text: str, out: Path, voice_id: str) -> tuple[float, list]:
    import requests

    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"},
        json={"text": _speakable(text), "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    out.write_bytes(base64.b64decode(data["audio_base64"]))
    dur = _duration(out)
    al = data.get("alignment") or {}
    chars, starts = al.get("characters") or [], al.get("character_start_times_seconds") or []
    if not chars:
        return dur, _estimate_words(text, dur)
    spoken = "".join(chars)
    words, pos = [], 0
    for w in text.split():
        idx = spoken.find(w[0], pos) if w else -1
        idx = pos if idx < 0 else idx
        words.append((w, starts[min(idx, len(starts) - 1)]))
        pos = idx + len(w)
    return dur, words


def synth_voice(text: str, out: Path, cfg: dict) -> tuple[float, list]:
    """Genera la voz de una escena. Devuelve (duración_s, [(palabra, inicio_s)])."""
    prov = cfg.get("provider", "auto")
    if prov in ("auto", "elevenlabs") and os.environ.get("ELEVENLABS_API_KEY") and cfg.get("elevenlabs_voice_id"):
        try:
            return tts_elevenlabs(text, out, cfg["elevenlabs_voice_id"])
        except Exception as e:  # noqa: BLE001
            print(f"[voz] ElevenLabs falló ({e}); paso a edge-tts")
    if prov in ("auto", "edge", "elevenlabs"):
        try:
            return tts_edge(text, out, cfg.get("edge_voice", "es-ES-AlvaroNeural"), cfg.get("edge_rate", "+6%"))
        except Exception as e:  # noqa: BLE001
            if prov == "edge":
                raise
            print(f"[voz] edge-tts no disponible ({type(e).__name__}); vídeo sin voz")
    dur = max(2.0, len(text.split()) / 2.9)
    return dur, _estimate_words(text, dur)


# ---------------- efectos (equivalentes a los del episodio 1) ----------------

def _tone(buf, at, f1, f2, d, kind="sine", vol=0.1):
    n = int(d * SR)
    s0 = int(at * SR)
    if s0 >= len(buf) or n <= 0:
        return
    n = min(n, len(buf) - s0)
    t = np.arange(n) / SR
    freq = f1 * (f2 / f1) ** (t / d)
    ph = 2 * np.pi * np.cumsum(freq) / SR
    if kind == "square":
        w = np.sign(np.sin(ph))
    elif kind == "triangle":
        w = 2 / np.pi * np.arcsin(np.sin(ph))
    else:
        w = np.sin(ph)
    env = vol * np.exp(np.log(0.001 / 1) * t / d)
    buf[s0:s0 + n] += w * env


def _noise(buf, at, d, vol=0.05):
    s0, n = int(at * SR), int(d * SR)
    n = min(n, len(buf) - s0)
    if n > 0:
        env = np.linspace(1, 0, n) ** 2
        buf[s0:s0 + n] += np.random.default_rng(1).uniform(-1, 1, n) * env * vol


FX = {
    "thud": lambda b, a: _tone(b, a + .85, 150, 45, .32, "sine", .7),
    "deflate": lambda b, a: _tone(b, a + .5, 520, 150, 1.4, "sine", .12),
    "print": lambda b, a: [_tone(b, a + .2 + i * .11, 2200, 1800, .03, "square", .03) for i in range(10)],
    "deal": lambda b, a: [_tone(b, a + .3 + d, 300, 1200, .12, "triangle", .08) for d in (0, .4, .8)],
    "hit": lambda b, a: _tone(b, a + .2, 110, 40, .45, "sine", .8),
    "hit2": lambda b, a: (_tone(b, a + .3, 110, 40, .45, "sine", .7), _tone(b, a + 1.9, 90, 35, .5, "sine", .8)),
    "rise": lambda b, a: (_tone(b, a + 1.1, 260, 880, .6, "triangle", .07), _tone(b, a + 2.8, 880, 260, .6, "triangle", .07)),
    "ding": lambda b, a: [(_tone(b, a + d, 1320, 1320, .25, "sine", .1), _tone(b, a + d + .08, 1760, 1760, .35, "sine", .08)) for d in (1, 3.2)],
    "cling": lambda b, a: (_tone(b, a + .4, 1800, 1800, .35, "sine", .12), _tone(b, a + .49, 2500, 2500, .45, "sine", .1)),
    "tick": lambda b, a: _tone(b, a, 900, 500, .07, "triangle", .07),
    "whoosh": lambda b, a: _noise(b, a + .1, .5, .06),
    "coins": lambda b, a: [_tone(b, a + .3 + i * .12, 2600 - i * 40, 2300, .06, "triangle", .05) for i in range(10)],
    "pop": lambda b, a: _tone(b, a + .2, 600, 1400, .08, "sine", .12),
}


def build_mix(timeline: dict, scenes: list, voice_files: list, out_wav: Path, fx_on: bool = True, voice_gain: float = 1.0,
              music_volume: float = 0.0, music_duck: float = 0.45, music_variant: int = 0):
    total = timeline["total"]
    buf = np.zeros(int((total + 0.5) * SR), dtype=np.float64)
    tmp = out_wav.with_suffix(".voice.wav")
    for sc_tl, f in zip(timeline["scenes"], voice_files):
        if not f or not Path(f).exists():
            continue
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-ac", "1", "-ar", str(SR), str(tmp)], check=True)
        with wave.open(str(tmp)) as w:
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        s0 = int((sc_tl["start"] + sc_tl["lead"]) * SR)
        n = min(len(data), len(buf) - s0)
        buf[s0:s0 + n] += data[:n] * voice_gain
    if music_volume > 0:
        from . import music
        bed = music.generate(len(buf) / SR, music_variant)[: len(buf)]
        bed = np.pad(bed, (0, len(buf) - len(bed)))
        buf += music.duck(bed, buf, music_duck) * music_volume
    if fx_on:
        for sc_tl, s in zip(timeline["scenes"], scenes):
            fx = s.get("sfx")
            if fx in FX:
                FX[fx](buf, sc_tl["start"])
    peak = np.max(np.abs(buf)) or 1
    if peak > 0.98:
        buf *= 0.98 / peak
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())
    if tmp.exists():
        tmp.unlink()
    return out_wav
