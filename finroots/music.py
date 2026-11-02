"""Música de fondo original (sin derechos de terceros), generada para cada episodio.

Base lo-fi cálida: acordes de pad, bajo y percusión suave. Cada episodio usa una variante
(progresión y tempo) para no repetir siempre lo mismo. La música baja sola cuando habla la voz.
"""
from __future__ import annotations

import numpy as np

SR = 44100

# (bpm, progresión de acordes en semitonos sobre La2=110 Hz)
PRESETS = [
    (96, [[0, 3, 7, 10, 14], [-4, 0, 3, 7, 11], [3, 7, 10, 14, 15], [-2, 2, 5, 9, 14]]),   # Am9 Fmaj7 Cmaj7 G6
    (100, [[5, 9, 12, 16], [0, 3, 7, 10], [-2, 2, 5, 9], [3, 7, 10, 14]]),                  # Dm-ish, positivo
    (92, [[-4, 0, 3, 7], [3, 7, 10, 14], [-2, 2, 5, 9], [0, 3, 7, 10]]),                    # F C G Am
    (104, [[0, 4, 7, 11], [5, 9, 12, 16], [2, 5, 9, 12], [7, 11, 14, 17]]),                 # mayor, alegre
]


def _f(semi: float) -> float:
    return 110.0 * 2 ** (semi / 12)


def _lowpass(x: np.ndarray, taps: int = 9) -> np.ndarray:
    k = np.hanning(taps)
    return np.convolve(x, k / k.sum(), mode="same")


def generate(seconds: float, variant: int = 0) -> np.ndarray:
    bpm, prog = PRESETS[variant % len(PRESETS)]
    beat = 60.0 / bpm
    bar = 4 * beat
    n = int((seconds + 1) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    rng = np.random.default_rng(variant + 7)

    # Pad: cada acorde dura 2 compases, con ataque y caída suaves
    chord_len = 2 * bar
    for ci in range(int(seconds / chord_len) + 2):
        notes = prog[ci % len(prog)]
        s0 = int(ci * chord_len * SR)
        L = int(chord_len * SR * 1.1)
        if s0 >= n:
            break
        L = min(L, n - s0)
        tt = np.arange(L) / SR
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (chord_len * 1.1 - tt) / 0.8)
        seg = np.zeros(L)
        for k, semi in enumerate(notes):
            f = _f(semi + 12)
            seg += (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)) / (1 + 0.3 * k)
        out[s0:s0 + L] += 0.18 * seg * env
        # Bajo: raíz en los tiempos 1 y 3
        root = _f(notes[0] - 12)
        for b in range(8):
            if b % 2:
                continue
            bs = s0 + int(b * beat * SR)
            BL = min(int(beat * 1.6 * SR), n - bs)
            if BL <= 0:
                continue
            bt = np.arange(BL) / SR
            out[bs:bs + BL] += 0.30 * np.sin(2 * np.pi * root * bt) * np.exp(-bt * 2.2)

    # Percusión suave
    for b in range(int(seconds / beat) + 1):
        bs = int(b * beat * SR)
        if bs >= n:
            break
        if b % 4 in (0, 2):  # bombo
            KL = min(int(0.22 * SR), n - bs)
            kt = np.arange(KL) / SR
            freq = 50 + 70 * np.exp(-kt * 30)
            out[bs:bs + KL] += 0.55 * np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-kt * 14)
        if b % 4 in (1, 3):  # chasquido
            CL = min(int(0.12 * SR), n - bs)
            noise = rng.uniform(-1, 1, CL)
            out[bs:bs + CL] += 0.12 * noise * np.exp(-np.arange(CL) / SR * 40)
        for h in (0, 0.5):  # charles en corcheas
            hs = bs + int(h * beat * SR)
            HL = min(int(0.04 * SR), n - hs)
            if HL <= 0:
                continue
            hn = rng.uniform(-1, 1, HL)
            hn = hn - np.concatenate([[0], hn[:-1]])  # paso alto simple
            out[hs:hs + HL] += 0.05 * hn * np.exp(-np.arange(HL) / SR * 90)

    out = out[: int(seconds * SR)]
    out = _lowpass(out)  # suaviza: sonido cálido tipo lo-fi
    fade_in, fade_out = int(0.6 * SR), int(2.0 * SR)
    out[:fade_in] *= np.linspace(0, 1, fade_in)
    out[-fade_out:] *= np.linspace(1, 0, fade_out)
    peak = np.max(np.abs(out)) or 1
    return out / peak


def duck(music: np.ndarray, voice: np.ndarray, amount: float = 0.45) -> np.ndarray:
    """Baja la música mientras suena la voz (con transiciones suaves)."""
    win = int(0.05 * SR)
    env = np.sqrt(np.convolve(voice[: len(music)] ** 2, np.ones(win) / win, mode="same"))
    active = np.clip(env / 0.03, 0, 1)
    k = int(0.25 * SR)
    active = np.convolve(active, np.ones(k) / k, mode="same")
    if len(active) < len(music):
        active = np.pad(active, (0, len(music) - len(active)))
    return music * (1 - amount * active)
