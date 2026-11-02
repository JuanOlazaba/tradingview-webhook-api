"""Iconos de Jarvis dibujados en Python puro (sin Pillow ni archivos binarios)."""
import math
import struct
import zlib

BG = (11, 15, 23)
RING = (56, 189, 248)
INNER = (14, 116, 144)
LETTER = (224, 242, 254)


def _ring(x, y, r, w):
    """Distancia (con signo) a un anillo centrado en (0.5, 0.5)."""
    return abs(math.hypot(x - 0.5, y - 0.5) - r) - w / 2


def _letter_j(x, y):
    """Distancia (con signo) a una letra J estilizada."""
    w = 0.075
    # Trazo vertical
    cx, top, bottom = 0.555, 0.335, 0.565
    dx = abs(x - cx) - w / 2
    dy = max(top - y, y - bottom)
    stem = math.hypot(max(dx, 0), max(dy, 0)) + min(max(dx, dy), 0)
    # Curva inferior (media circunferencia hacia abajo)
    r, ccx, ccy = 0.085, cx - 0.085, bottom
    if y >= ccy:
        hook = abs(math.hypot(x - ccx, y - ccy) - r) - w / 2
    else:
        hook = math.hypot(x - (ccx - r), y - ccy) - w / 2
    return min(stem, hook)


def _blend(base, color, a):
    return tuple(round(b + (c - b) * a) for b, c in zip(base, color))


def render(size):
    aa = 1.2 / size
    rows = []
    for py in range(size):
        y = (py + 0.5) / size
        row = bytearray(b"\x00")
        for px in range(size):
            x = (px + 0.5) / size
            col = BG
            for d, color in (
                (_ring(x, y, 0.36, 0.035), RING),
                (_ring(x, y, 0.26, 0.018), INNER),
                (_letter_j(x, y), LETTER),
            ):
                a = min(1.0, max(0.0, 0.5 - d / aa))
                if a:
                    col = _blend(col, color, a)
            row += bytes(col)
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
        + chunk(b"IEND", b"")
    )


SIZES = {"icon-180.png": 180, "icon-192.png": 192, "icon-512.png": 512}
_cache = {}


def get_icon(name):
    """Devuelve los bytes PNG del icono, o None si no existe."""
    if name not in SIZES:
        return None
    if name not in _cache:
        _cache[name] = render(SIZES[name])
    return _cache[name]
