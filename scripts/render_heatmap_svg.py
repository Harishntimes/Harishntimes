"""data/contributions.json -> contrib-heatmap.svg (53x7 grid, one-time diagonal reveal)."""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, DIM, TXT, MUTED = "#0d1117", "#30363d", "#c9d1d9", "#8b949e"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

CELL, GAP = 15, 4
X0, Y0 = 52, 58
W, H = 1100, 290

data = json.loads((ROOT / "data" / "contributions.json").read_text())
days = data["days"]
first = date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
    f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{DIM}"/>',
    '<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/>'
    '<circle cx="50" cy="16" r="5" fill="#27c93f"/>',
    f'<text x="{W / 2}" y="20" fill="{MUTED}" font-size="11" text-anchor="middle">'
    f'{data["total"]} contribution{"" if data["total"] == 1 else "s"} in the last year</text>',
]

# weekday + month labels
for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    out.append(f'<text x="{X0 - 8}" y="{Y0 + r * (CELL + GAP) + 12}" font-size="11" fill="{MUTED}" text-anchor="end">{name}</text>')
last_month = None
for i, d in enumerate(days):
    col, row = divmod(i + offset, 7)
    m = d["date"][:7]
    if (row == 0 or i == 0) and m != last_month:
        label = date.fromisoformat(d["date"]).strftime("%b")
        out.append(f'<text x="{X0 + col * (CELL + GAP)}" y="{Y0 - 10}" font-size="11" fill="{MUTED}">{label}</text>')
        last_month = m

for i, d in enumerate(days):
    col, row = divmod(i + offset, 7)
    x, y = X0 + col * (CELL + GAP), Y0 + row * (CELL + GAP)
    fill = PALETTE[min(d["level"], 4) if d["count"] < 20 else 5]
    title = f'<title>{d["count"]} on {d["date"]}</title>'
    if STATIC:
        out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}">{title}</rect>')
        continue
    b = 0.3 + (col + row) * 0.025  # diagonal wave
    out.append(
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}" opacity="0">{title}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{b:.3f}s" dur="0.35s" fill="freeze"/>'
        f'<animate attributeName="y" from="{y - 10}" to="{y}" begin="{b:.3f}s" dur="0.35s" fill="freeze"/>'
        f"</rect>"
    )

# legend
ly = Y0 + 7 * (CELL + GAP) + 14
lx = W - 40 - len(PALETTE) * (CELL + 3) - 40
out.append(f'<text x="{lx - 8}" y="{ly + 12}" font-size="11" fill="{MUTED}" text-anchor="end">Less</text>')
for j, c in enumerate(PALETTE):
    out.append(f'<rect x="{lx + j * (CELL + 3)}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
out.append(f'<text x="{lx + len(PALETTE) * (CELL + 3) + 4}" y="{ly + 12}" font-size="11" fill="{MUTED}">More</text>')

# stats footer
best = data["best_day"]
best_s = f'{best["count"]} on {date.fromisoformat(best["date"]).strftime("%b %d")}' if best["count"] else "—"
busiest = max(data["monthly"].items(), key=lambda kv: kv[1])
stats = [
    ("current streak", f'{data["current_streak"]}d'),
    ("longest streak", f'{data["longest_streak"]}d'),
    ("best day", best_s),
    ("busiest month", f'{date.fromisoformat(busiest[0] + "-01").strftime("%b %Y")} ({busiest[1]})'),
]
fy = H - 26
out.append(f'<line x1="24" y1="{fy - 24}" x2="{W - 24}" y2="{fy - 24}" stroke="{DIM}"/>')
for k, (label, val) in enumerate(stats):
    x = 40 + k * 260
    out.append(
        f'<text x="{x}" y="{fy}" font-size="13"><tspan fill="{MUTED}">{label}: </tspan>'
        f'<tspan fill="{PALETTE[4]}" font-weight="bold">{val}</tspan></text>'
    )

out.append("</svg>")
(ROOT / "contrib-heatmap.svg").write_text("\n".join(out))
print("wrote contrib-heatmap.svg")
