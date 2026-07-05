#!/usr/bin/env python3
"""Generate the Exam Email Automation application icon.

Replicates the blue-envelope design from gui/icon.py using Pillow (no Qt dependency).
Outputs multi-resolution .ico for Windows, .png for About dialog, and .icns for macOS.

Usage:
    python3 scripts/generate_icon.py
"""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install pillow")
    raise SystemExit(1)


RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"

# --- Icon design (drawn at 256x256 base, then scaled down for multi-resolution) ---
BASE_SIZE = 256
SCALE = BASE_SIZE / 64  # Original Qt design was at 64x64


def _draw_envelope(draw: ImageDraw.ImageDraw, size: int) -> None:
    """Draw the blue envelope + white checkmark onto the given draw context."""
    s = size / 64  # scale factor relative to the original 64x64 coordinate space

    # Blue rounded rectangle (envelope body)
    x, y, w, h = int(4 * s), int(14 * s), int(56 * s), int(38 * s)
    radius = int(6 * s)
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=radius,
        fill="#2563eb",
    )

    # Envelope flap (triangle)
    flap = [
        (int(4 * s), int(14 * s)),
        (int(32 * s), int(38 * s)),
        (int(60 * s), int(14 * s)),
    ]
    draw.polygon(flap, fill="#3b82f6")

    # Darker flap edge line
    draw.line(
        [(int(4 * s), int(14 * s)), (int(32 * s), int(38 * s))],
        fill="#1d4ed8",
        width=max(1, int(2 * s)),
    )

    # White checkmark
    line_width = max(2, int(3 * s))
    draw.line(
        [(int(18 * s), int(34 * s)), (int(28 * s), int(44 * s))],
        fill="#ffffff",
        width=line_width,
    )
    draw.line(
        [(int(28 * s), int(44 * s)), (int(46 * s), int(26 * s))],
        fill="#ffffff",
        width=line_width,
    )


def generate_png(size: int, path: Path) -> None:
    """Generate a single PNG at the given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _draw_envelope(draw, size)
    img.save(path, "PNG")
    print(f"  Created: {path} ({size}x{size})")


def generate_ico(sizes: list[int], path: Path) -> None:
    """Generate a multi-resolution .ico file."""
    images: list[Image.Image] = []
    for size in sorted(sizes, reverse=True):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        _draw_envelope(draw, size)
        images.append(img)

    # Save as .ico with multiple sizes
    images[0].save(
        path,
        format="ICO",
        sizes=[(s, s) for s in sorted(sizes)],
        append_images=images[1:],
    )
    print(f"  Created: {path} (sizes: {sizes})")


def main() -> None:
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating Exam Email Automation icons...")

    # Multi-resolution .ico for Windows (taskbar, desktop, explorer)
    generate_ico([16, 32, 48, 256], RESOURCES_DIR / "icon.ico")

    # Single 256x256 PNG for About dialog and other uses
    generate_png(256, RESOURCES_DIR / "icon.png")

    print("Done.")


if __name__ == "__main__":
    main()
