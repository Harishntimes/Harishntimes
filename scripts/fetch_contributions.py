"""Scrape the public contributions calendar (no API, no token) -> data/contributions.json."""
import json
import re
from collections import OrderedDict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = "Harishntimes"
ROOT = Path(__file__).resolve().parent.parent

html = requests.get(f"https://github.com/users/{USER}/contributions", timeout=30).text
soup = BeautifulSoup(html, "html.parser")

counts = {}
for tip in soup.select("tool-tip[for]"):
    m = re.match(r"(\d+|No) contributions?", tip.get_text(strip=True))
    if m:
        counts[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1))

days = []
for td in soup.select("td.ContributionCalendar-day[data-date]"):
    days.append({
        "date": td["data-date"],
        "level": int(td.get("data-level", 0)),
        "count": counts.get(td.get("id"), 0),
    })
days.sort(key=lambda d: d["date"])
if not days:
    raise SystemExit("no contribution cells found - GitHub markup may have changed")

# streaks
longest = run = 0
prev = None
for d in days:
    cur = date.fromisoformat(d["date"])
    if d["count"] > 0:
        run = run + 1 if prev and cur - prev == timedelta(days=1) else 1
        prev = cur
        longest = max(longest, run)
    else:
        prev = None
        run = 0

current = 0
tail = list(reversed(days))
if tail and tail[0]["count"] == 0:  # today not counted yet doesn't break the streak
    tail = tail[1:]
for d in tail:
    if d["count"] == 0:
        break
    current += 1

best = max(days, key=lambda d: d["count"])
monthly = OrderedDict()
for d in days:
    monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]

data = {
    "user": USER,
    "total": sum(d["count"] for d in days),
    "current_streak": current,
    "longest_streak": longest,
    "best_day": {"date": best["date"], "count": best["count"]},
    "monthly": monthly,
    "days": days,
}
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "contributions.json").write_text(json.dumps(data, indent=1))
print(f"{len(days)} days, {data['total']} contributions, streak {current}/{longest}")
