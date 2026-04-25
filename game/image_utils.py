"""
image_utils.py - Small helpers for image manipulation using Pillow.

Provides `recolor_flask_image` which replaces a source hex color (default
`#00A8F3`) with a target hex color in an image and writes the result.
"""
from PIL import Image
import pygame


def _hex_to_rgba(hex_str: str) -> tuple:
    s = hex_str.lstrip('#')
    if len(s) == 6:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        a = 255
    elif len(s) == 8:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        a = int(s[6:8], 16)
    else:
        raise ValueError("Invalid hex color")
    return (r, g, b, a)


def recolor_flask_image(input_path: str, output_path: str, target_hex: str, source_hex: str = "#00A8F3", tolerance: int = 0) -> None:
    """
    Replace pixels matching `source_hex` in `input_path` with `target_hex` and save to `output_path`.

    Args:
        input_path: Path to source image (any Pillow-supported format).
        output_path: Path to write recolored image.
        target_hex: Replacement color (e.g., '#FF0000').
        source_hex: Color to replace (default '#00A8F3').
        tolerance: Integer 0-255 allowing approximate matches (Euclidean distance in RGB).
    """
    src_rgba = _hex_to_rgba(source_hex)
    tgt_rgba = _hex_to_rgba(target_hex)

    img = Image.open(input_path).convert('RGBA')
    pixels = img.load()
    w, h = img.size

    def close_enough(px, target, tol):
        return ((px[0] - target[0]) ** 2 + (px[1] - target[1]) ** 2 + (px[2] - target[2]) ** 2) <= tol * tol

    for y in range(h):
        for x in range(w):
            p = pixels[x, y]
            # Only replace non-transparent pixels (alpha > 0)
            if p[3] == 0:
                continue
            if tolerance <= 0:
                if p[0:3] == src_rgba[0:3]:
                    pixels[x, y] = (tgt_rgba[0], tgt_rgba[1], tgt_rgba[2], p[3])
            else:
                if close_enough(p, src_rgba, tolerance):
                    pixels[x, y] = (tgt_rgba[0], tgt_rgba[1], tgt_rgba[2], p[3])

    img.save(output_path)


def recolor_image_to_surface(input_path: str, target_hex: str, source_hex: str = "#00A8F3", tolerance: int = 0) -> 'pygame.Surface':
    """
    Recolor an image (replace source_hex with target_hex) and return a pygame Surface.
    Does not write files to disk.
    """
    src_rgba = _hex_to_rgba(source_hex)
    tgt_rgba = _hex_to_rgba(target_hex)

    pil = Image.open(input_path).convert('RGBA')
    pixels = pil.load()
    w, h = pil.size

    def close_enough(px, target, tol):
        return ((px[0] - target[0]) ** 2 + (px[1] - target[1]) ** 2 + (px[2] - target[2]) ** 2) <= tol * tol

    for y in range(h):
        for x in range(w):
            p = pixels[x, y]
            if p[3] == 0:
                continue
            if tolerance <= 0:
                if p[0:3] == src_rgba[0:3]:
                    pixels[x, y] = (tgt_rgba[0], tgt_rgba[1], tgt_rgba[2], p[3])
            else:
                if close_enough(p, src_rgba, tolerance):
                    pixels[x, y] = (tgt_rgba[0], tgt_rgba[1], tgt_rgba[2], p[3])

    raw = pil.tobytes()
    surf = pygame.image.frombuffer(raw, pil.size, 'RGBA').convert_alpha()
    return surf
