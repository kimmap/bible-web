#!/usr/bin/env python3
"""Generate a simple Bible Web app icon as a real PNG."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


SIZE = 512
OUT = Path(__file__).resolve().parents[1] / "app-icon.png"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def clamp(v: float) -> int:
    return max(0, min(255, int(round(v))))


def fill_rect(pixels, x0, y0, x1, y1, color, alpha=1.0):
    x0 = max(0, int(math.floor(x0)))
    y0 = max(0, int(math.floor(y0)))
    x1 = min(SIZE, int(math.ceil(x1)))
    y1 = min(SIZE, int(math.ceil(y1)))
    r, g, b = color
    for y in range(y0, y1):
        row = pixels[y]
        for x in range(x0, x1):
            pr, pg, pb, pa = row[x]
            inv = 1.0 - alpha
            row[x] = (
                clamp(pr * inv + r * alpha),
                clamp(pg * inv + g * alpha),
                clamp(pb * inv + b * alpha),
                255,
            )


def fill_rounded_rect(pixels, x0, y0, x1, y1, radius, color, alpha=1.0):
    r, g, b = color
    radius = float(radius)
    for y in range(max(0, int(y0)), min(SIZE, int(y1))):
        for x in range(max(0, int(x0)), min(SIZE, int(x1))):
            dx = 0.0
            dy = 0.0
            if x < x0 + radius:
                dx = x0 + radius - x
            elif x > x1 - radius:
                dx = x - (x1 - radius)
            if y < y0 + radius:
                dy = y0 + radius - y
            elif y > y1 - radius:
                dy = y - (y1 - radius)
            if dx * dx + dy * dy <= radius * radius:
                pr, pg, pb, pa = pixels[y][x]
                inv = 1.0 - alpha
                pixels[y][x] = (
                    clamp(pr * inv + r * alpha),
                    clamp(pg * inv + g * alpha),
                    clamp(pb * inv + b * alpha),
                    255,
                )


def fill_ellipse(pixels, cx, cy, rx, ry, color, alpha=1.0):
    r, g, b = color
    x0 = max(0, int(cx - rx))
    x1 = min(SIZE, int(cx + rx) + 1)
    y0 = max(0, int(cy - ry))
    y1 = min(SIZE, int(cy + ry) + 1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            nx = (x - cx) / rx
            ny = (y - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                pr, pg, pb, pa = pixels[y][x]
                inv = 1.0 - alpha
                pixels[y][x] = (
                    clamp(pr * inv + r * alpha),
                    clamp(pg * inv + g * alpha),
                    clamp(pb * inv + b * alpha),
                    255,
                )


def fill_line_h(pixels, x0, x1, y, thickness, color, alpha=1.0):
    fill_rect(pixels, x0, y - thickness / 2, x1, y + thickness / 2, color, alpha)


def fill_line_v(pixels, x, y0, y1, thickness, color, alpha=1.0):
    fill_rect(pixels, x - thickness / 2, y0, x + thickness / 2, y1, color, alpha)


def to_png(path: Path, pixels):
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b, a in row:
            raw.extend(bytes((r, g, b, a)))
    compressed = zlib.compress(bytes(raw), level=9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = bytearray()
    png.extend(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)))
    png.extend(chunk(b"IDAT", compressed))
    png.extend(chunk(b"IEND", b""))
    path.write_bytes(bytes(png))


def main():
    bg_top = hex_to_rgb("#f4efe6")
    bg_bottom = hex_to_rgb("#dcc8ab")
    shadow = hex_to_rgb("#92724c")
    book = hex_to_rgb("#7b5e3d")
    book_edge = hex_to_rgb("#5d452b")
    paper = hex_to_rgb("#fbf7ef")
    paper_edge = hex_to_rgb("#d7c8b1")
    ink = hex_to_rgb("#8c6a46")
    gold = hex_to_rgb("#d4a23e")
    highlight = hex_to_rgb("#fff7ea")

    pixels = [[(*bg_top, 255) for _ in range(SIZE)] for _ in range(SIZE)]
    cx = cy = SIZE / 2

    for y in range(SIZE):
        t = y / (SIZE - 1)
        for x in range(SIZE):
            radial = math.hypot(x - cx, y - cy) / (SIZE * 0.75)
            mix = min(1.0, 0.18 + 0.82 * max(t, radial))
            r = clamp(bg_top[0] * (1 - mix) + bg_bottom[0] * mix)
            g = clamp(bg_top[1] * (1 - mix) + bg_bottom[1] * mix)
            b = clamp(bg_top[2] * (1 - mix) + bg_bottom[2] * mix)
            pixels[y][x] = (r, g, b, 255)

    fill_ellipse(pixels, 266, 336, 140, 42, shadow, alpha=0.18)
    fill_ellipse(pixels, 246, 176, 110, 95, highlight, alpha=0.10)

    fill_rounded_rect(pixels, 84, 92, 428, 428, 56, book_edge, alpha=0.35)
    fill_rounded_rect(pixels, 76, 84, 420, 420, 56, book, alpha=1.0)
    fill_rounded_rect(pixels, 98, 106, 398, 398, 46, paper, alpha=1.0)

    fill_rect(pixels, 245, 116, 267, 394, paper_edge, alpha=0.9)
    fill_line_v(pixels, 256, 118, 392, 4, book_edge, alpha=0.7)

    for y in (160, 190, 220, 250, 280):
        fill_line_h(pixels, 128, 236, y, 4, ink, alpha=0.45)
        fill_line_h(pixels, 276, 384, y, 4, ink, alpha=0.45)

    # Cross
    fill_rect(pixels, 245, 126, 267, 176, gold, alpha=1.0)
    fill_rect(pixels, 228, 143, 284, 159, gold, alpha=1.0)
    fill_rounded_rect(pixels, 238, 120, 274, 156, 8, gold, alpha=0.18)

    to_png(OUT, pixels)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
