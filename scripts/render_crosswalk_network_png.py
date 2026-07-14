#!/usr/bin/env python3
"""Render docs/crosswalks/crosswalk-network.png by SCREENSHOTTING the D3 figure.

The PNG is now a rasterisation of `crosswalk-network.html` itself, taken in
headless Chrome, rather than an independent redraw. It previously re-implemented
the whole figure in matplotlib + networkx — a SECOND layout of the same data,
which meant a second thing to keep in sync and, in practice, a worse picture: the
networkx `spring_layout` has no notion of label collision, so the biomedical
cluster's names printed straight through one another. The D3 page already solves
that (label-aware collision radii, domain clustering, fit-to-viewport), so the
honest thing is to photograph it instead of imitating it.

This is only reproducible because the page settles its force simulation
SYNCHRONOUSLY at load (see the "Settle the layout SYNCHRONOUSLY" comment there):
the geometry does not depend on animation timing, so the same HTML always yields
the same PNG. The page is loaded with `?static=1`, which hides the controls that
only mean something when you can click them (the interaction hint, reset button).

Requires Google Chrome. Run after build_crosswalk_network.py:

    python scripts/render_crosswalk_network_png.py
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "docs" / "crosswalks" / "crosswalk-network.html"
PNG = ROOT / "docs" / "crosswalks" / "crosswalk-network.png"

# 2x device scale => a crisp retina PNG; the page is laid out for ~1500px wide.
WIDTH, HEIGHT, SCALE = 1500, 1150, 2

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
]


def find_chrome() -> str:
    for cand in CHROME_CANDIDATES:
        if Path(cand).exists():
            return cand
        found = shutil.which(cand)
        if found:
            return found
    sys.exit(
        "Google Chrome not found — needed to rasterise the D3 figure.\n"
        "Install Chrome, or set one of: " + ", ".join(CHROME_CANDIDATES)
    )


def trim(im: Image.Image) -> Image.Image:
    """Crop the uniform page-background border so the PNG is all figure."""
    rgb = im.convert("RGB")
    bg = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
    from PIL import ImageChops

    box = ImageChops.difference(rgb, bg).getbbox()
    if not box:
        return im
    pad = 8 * SCALE
    x0, y0, x1, y1 = box
    return im.crop(
        (
            max(0, x0 - pad),
            max(0, y0 - pad),
            min(im.width, x1 + pad),
            min(im.height, y1 + pad),
        )
    )


def main() -> int:
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        shot = Path(tmp) / "shot.png"
        # NB: do NOT pass --user-data-dir. Pointing Chrome at a fresh profile
        # directory makes headless hang indefinitely here (it never gets past
        # profile setup, even with --no-first-run); the default profile screenshots
        # in ~2s. The timeout turns any future hang into a loud failure rather than
        # a wedged build.
        try:
            subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    f"--force-device-scale-factor={SCALE}",
                    f"--window-size={WIDTH},{HEIGHT}",
                    f"--screenshot={shot}",
                    f"file://{HTML}?static=1",
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            sys.exit("Chrome timed out rendering the figure (>120s)")
        if not shot.exists():
            sys.exit("Chrome produced no screenshot")
        im = trim(Image.open(shot))

        # Stamp the sha256 of the SOURCE html into a PNG tEXt chunk. A test asserts
        # this still matches the current HTML, so a stale PNG (rendered before a
        # crosswalk edit) fails CI instead of silently shipping a figure that
        # disagrees with the table. Byte-comparing a fresh render would be hostage
        # to the browser version; the stamp is not.
        src = hashlib.sha256(HTML.read_bytes()).hexdigest()
        meta = PngImagePlugin.PngInfo()
        meta.add_text("Description", src)
        im.save(PNG, optimize=True, pnginfo=meta)

    print(
        f"wrote {PNG.relative_to(ROOT)} — {im.width}x{im.height} "
        f"(rasterised from crosswalk-network.html, sha256 {src[:12]}…)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
