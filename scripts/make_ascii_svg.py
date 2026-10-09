"""source-prepped.png -> ascii-portrait.svg, a self-typing monochrome portrait.

Each row is revealed by a left-to-right clip wipe with a block cursor,
staggered top to bottom; the final frame freezes.
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

COLS, ROWS = 100, 56
RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)
FONT, CW, LH = 10, 6.0, 11  # font size, char width, line height
PAD_X, PAD_TOP, PAD_BOTTOM = 16, 40, 16
ROW_DUR, ROW_GAP, START = 0.35, 0.07, 0.4  # seconds
STATIC = os.environ.get("STATIC") == "1"

BG, FG, DIM = "#0d1117", "#c9d1d9", "#30363d"

img = Image.open(ROOT / "source-prepped.png").convert("L").resize((COLS, ROWS), Image.LANCZOS)
px = np.asarray(img, dtype=np.float32) / 255.0
px = np.clip((px - 0.08) / 0.84, 0, 1)  # stretch so the background goes fully blank

lines = []
for row in px:
    idx = ((1 - row) * (len(RAMP) - 1)).round().astype(int)
    # non-breaking spaces so renderers keep the gaps inside each row
    lines.append("".join(RAMP[i] for i in idx).replace(" ", "\u00a0"))

text_w = COLS * CW
W = int(text_w + 2 * PAD_X)
H = int(PAD_TOP + ROWS * LH + PAD_BOTTOM)

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{DIM}"/>',
    '<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/>'
    '<circle cx="50" cy="16" r="5" fill="#27c93f"/>',
    f'<text x="{W / 2}" y="20" fill="#8b949e" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
    f'font-size="11" text-anchor="middle">harish@ntimes ~ $ cat portrait.txt</text>',
    f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT}" fill="{FG}" xml:space="preserve">',
]
defs = ["<defs>"]

for i, line in enumerate(lines):
    if not line.replace("\u00a0", ""):
        continue
    y = PAD_TOP + i * LH
    lw = len(line) * CW
    attrs = f'x="{PAD_X}" y="{y + LH - 2}" textLength="{lw:.0f}" lengthAdjust="spacing"'
    if STATIC:
        out.append(f"<text {attrs}>{line}</text>")
        continue
    begin = START + i * ROW_GAP
    defs.append(
        f'<clipPath id="r{i}"><rect x="{PAD_X}" y="{y}" width="0" height="{LH}">'
        f'<animate attributeName="width" from="0" to="{lw:.0f}" begin="{begin:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
        f"</rect></clipPath>"
    )
    out.append(f'<text {attrs} clip-path="url(#r{i})">{line}</text>')
    # block cursor riding the wipe, gone once the row is done
    out.append(
        f'<rect x="{PAD_X}" y="{y + 1}" width="{CW}" height="{LH - 1}" fill="#39d353" opacity="0">'
        f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + lw:.0f}" begin="{begin:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{begin + ROW_DUR:.2f}s"/>'
        f"</rect>"
    )

defs.append("</defs>")
out.append("</g>")
svg = out[:2] + defs + out[2:] + ["</svg>"]
(ROOT / "ascii-portrait.svg").write_text("\n".join(svg))
print(f"wrote ascii-portrait.svg ({W}x{H})")
