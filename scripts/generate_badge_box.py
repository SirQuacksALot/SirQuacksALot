import os
import base64
import requests
from jinja2 import Template

WAKATIME_API_KEY = os.environ["WAKATIME_API_KEY"]

BADGES = [
    "Tea_addict",
    "coding_enthusiast",
    "C++ & Rust",
    "loves_to_experiment",
]

def fetch_wakatime():
    headers = {"Authorization": f"Bearer {WAKATIME_API_KEY}"}
    url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()["data"]
    total_seconds = data["total_seconds"]
    languages = data.get("languages", [])
    top_lang = languages[0]["name"] if languages else "n/a"
    return round(total_seconds / 3600, 1), top_lang

def main():
    hours, top_lang = fetch_wakatime()
    with open("templates/badge-box.svg.j2") as f:
        template = Template(f.read())
    total_height = len(BADGES) * 36 + 80
    svg = template.render(
        badges=BADGES,
        wakatime_hours=hours,
        wakatime_top_lang=top_lang,
        total_height=total_height,
    )
    os.makedirs("img", exist_ok=True)
    with open("img/badge-box.svg", "w") as f:
        f.write(svg)
    print(f"Wrote img/badge-box.svg ({hours}h, {top_lang})")

if __name__ == "__main__":
    main()