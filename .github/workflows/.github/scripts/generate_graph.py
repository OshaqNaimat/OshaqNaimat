import requests
import os
from datetime import datetime

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "OshaqNaimat"

query = """
{
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
""" % USERNAME

headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
data = response.json()

weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

days = []
for week in weeks:
    for day in week["contributionDays"]:
        days.append((day["date"][-2:].lstrip("0") or "0", day["contributionCount"]))

days = days[-30:]

max_val = max(c for _, c in days) or 1

W, H = 900, 300
pad_left = 60
pad_right = 20
pad_top = 50
pad_bottom = 50
chart_w = W - pad_left - pad_right
chart_h = H - pad_top - pad_bottom
n = len(days)

def x(i): return pad_left + i * chart_w // (n - 1)
def y(v): return pad_top + chart_h - int((v / max_val) * chart_h)

y_ticks = range(0, max_val + 2, max(1, max_val // 6))
grid = ""
for v in y_ticks:
    yy = y(v)
    grid += f'<line x1="{pad_left}" y1="{yy}" x2="{W - pad_right}" y2="{yy}" stroke="#1e3a5f" stroke-width="1" stroke-dasharray="4,4"/>\n'
    grid += f'<text x="{pad_left - 8}" y="{yy + 4}" text-anchor="end" fill="#4a7fa5" font-size="11" font-family="Arial">{v}</text>\n'

x_grid = ""
for i in range(n):
    xx = x(i)
    x_grid += f'<line x1="{xx}" y1="{pad_top}" x2="{xx}" y2="{pad_top + chart_h}" stroke="#1e3a5f" stroke-width="1" stroke-dasharray="4,4"/>\n'

points = [(x(i), y(c)) for i, (_, c) in enumerate(days)]
line_d = "M " + " L ".join(f"{px},{py}" for px, py in points)
area_d = f"M {points[0][0]},{pad_top + chart_h} L " + " L ".join(f"{px},{py}" for px, py in points) + f" L {points[-1][0]},{pad_top + chart_h} Z"

dots = ""
for px, py in points:
    dots += f'<circle cx="{px}" cy="{py}" r="3" fill="#a8c8e8" stroke="#0d1117" stroke-width="1.5"/>\n'

x_labels = ""
for i, (day_label, _) in enumerate(days):
    if i % 3 == 0:
        x_labels += f'<text x="{x(i)}" y="{H - 10}" text-anchor="middle" fill="#4a7fa5" font-size="11" font-family="Arial">{day_label}</text>\n'

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#58a6ff" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="#0d1117" rx="12"/>
  <text x="{W//2}" y="28" text-anchor="middle" fill="#58a6ff" font-size="16" font-family="Arial" font-weight="bold">Oshaq Naimat's Contribution Graph</text>
  <text x="14" y="{H//2}" text-anchor="middle" fill="#4a7fa5" font-size="12" font-family="Arial" transform="rotate(-90, 14, {H//2})">Contributions</text>
  <text x="{W//2}" y="{H - 2}" text-anchor="middle" fill="#4a7fa5" font-size="12" font-family="Arial">Days</text>
  {grid}
  {x_grid}
  <path d="{area_d}" fill="url(#areaGrad)"/>
  <path d="{line_d}" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  {dots}
  {x_labels}
</svg>"""

os.makedirs("dist", exist_ok=True)
with open("dist/contribution-graph.svg", "w") as f:
    f.write(svg)

print("Graph generated!")
