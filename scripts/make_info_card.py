"""Hand-authored neofetch-style info card -> info-card.svg.

Edit ROWS below to change what the card says. STATIC=1 renders a frozen frame.
"""
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

TITLE = "harish@ntimes"
ROWS = [
    ("User", "Harish · @Harishntimes"),
    ("Work", "AI engineer @ ntimes.ai"),
    ("Now", "Creative-intelligence RAG for AI video"),
    ("", "generation (OpenAI + ChromaDB)"),
    ("Built", "personaplex-backend · real-time voice"),
    ("", "agents on LiveKit · MCP tool servers"),
    ("Stack", "Python · TypeScript · React Native"),
    ("", "Kotlin · OpenAI · LiveKit · ChromaDB"),
    ("Video", "Veo 3.1 · Higgsfield · Sora"),
    ("Focus", "LLM apps, RAG, voice + video AI"),
    ("Mail", "harish@ntimes.ai"),
]

W, H = 600, 448
BG, DIM, KEY, VAL, ACCENT = "#0d1117", "#30363d", "#58a6ff", "#c9d1d9", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
X_KEY, X_VAL, Y0, LH = 28, 108, 92, 26


def fade(i):
    if STATIC:
        return "", ""
    b = 0.5 + i * 0.18
    return (
        ' opacity="0"',
        f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur="0.4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="-12 0" to="0 0" '
        f'begin="{b:.2f}s" dur="0.4s" fill="freeze"/>',
    )


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
    f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{DIM}"/>',
    '<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/>'
    '<circle cx="50" cy="16" r="5" fill="#27c93f"/>',
    f'<text x="{W / 2}" y="20" fill="#8b949e" font-size="11" text-anchor="middle">~ $ neofetch</text>',
]

op, anim = fade(0)
out.append(
    f'<g{op}><text x="{X_KEY}" y="60" font-size="17" font-weight="bold">'
    f'<tspan fill="{ACCENT}">{TITLE}</tspan></text>'
    f'<line x1="{X_KEY}" y1="70" x2="{W - 28}" y2="70" stroke="{DIM}"/>{anim}</g>'
)

for i, (k, v) in enumerate(ROWS, start=1):
    y = Y0 + (i - 1) * LH
    op, anim = fade(i)
    out.append(
        f'<g{op}><text y="{y}" font-size="14">'
        f'<tspan x="{X_KEY}" fill="{KEY}" font-weight="bold">{escape(k)}</tspan>'
        f'<tspan x="{X_VAL}" fill="{VAL}">{escape(v)}</tspan></text>{anim}</g>'
    )

# neofetch colour swatches + blinking prompt
y = Y0 + len(ROWS) * LH + 6
op, anim = fade(len(ROWS) + 1)
sw = "".join(
    f'<rect x="{X_KEY + j * 30}" y="{y - 12}" width="26" height="14" rx="2" fill="{c}"/>'
    for j, c in enumerate(["#f85149", "#d29922", "#3fb950", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9", "#6e7681"])
)
out.append(f"<g{op}>{sw}{anim}</g>")
blink = "" if STATIC else '<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
out.append(
    f'<text x="{X_KEY}" y="{H - 18}" font-size="14" fill="{ACCENT}">harish@ntimes ~ $ '
    f'<tspan fill="{VAL}">█{blink}</tspan></text>'
)
out.append("</svg>")

(ROOT / "info-card.svg").write_text("\n".join(out))
print("wrote info-card.svg")
