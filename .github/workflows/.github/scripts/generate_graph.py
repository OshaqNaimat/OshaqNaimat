import requests
import os
from datetime import datetime, timedelta
from collections import defaultdict

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

monthly = defaultdict(int)
for week in weeks:
    for day in week["contributionDays"]:
        month = day["date"][:7]  # YYYY-MM
        monthly[month] += day["contributionCount"]

sorted_months = sorted(monthly.items())[-12:]  # last 12 months

max_val = max(v for _, v in sorted_months) or 1

# SVG settings
W, H = 900, 300
padding = 50
bar_gap = 10
bar_width = (W - padding * 2 - bar_gap * (len(sorted_months) - 1)) // len(sorted_months)
chart_h = H - padding * 2

bars_svg = ""
labels_svg = ""
values_svg = ""

for i, (month, count) in enumerate(sorted_months):
    bar_h = int((count / max_val) * chart_h)
    x = padding + i * (bar_width + bar_gap)
    y = padding + chart_h - bar_h
    label = datetime.strptime(month, "%Y-%m").strftime("%b")

    bars_svg += f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" rx="4" fill="url(#barGrad)" opacity="0.9"/>\n'
    labels_svg += f'<text x="{x + bar_width // 2}" y="{H - 10}" text-anchor="middle" fill="#8b949e" font-size="12" font-family="Arial">{label}</text>\n'
    values_svg += f'<text x="{x + bar_width // 2}" y="{y - 6}" text-anchor="middle" fill="#58a6ff" font-size="11" font-family="Arial">{count}</text>\n'

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#1f6feb"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="#0d1117" rx="12"/>
  <text x="{W//2}" y="30" text-anchor="middle" fill="#e6edf3" font-size="15" font-family="Arial" font-weight="bold">Monthly Contributions</text>
  {bars_svg}
  {labels_svg}
  {values_svg}
</svg>"""

os.makedirs("dist", exist_ok=True)
with open("dist/contribution-graph.svg", "w") as f:
    f.write(svg)

print("Graph generated successfully!")
