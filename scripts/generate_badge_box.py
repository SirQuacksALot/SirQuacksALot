
import os
import copy
import requests
import xml.etree.ElementTree as ET

# --------------------------------------------------
# Configuration
# --------------------------------------------------

WAKATIME_TOKEN = os.environ["WAKATIME_API_KEY"]

BADGES = [
    ("Tea_addict", "mocha"),
    ("coding_enthusiast", "devbox"),
    ("loves_to_experiment", "i18next"),
    ("C++ & Rust", "southwestairlines"),
]

BLUE = "58a6ff"
TRANSPARENT = "24292f00"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

SESSION = requests.Session()


# --------------------------------------------------
# Fetch WakaTime statistics
# --------------------------------------------------

def fetch_wakatime():
    url = (
        "https://api.wakatime.com/api/v1/"
        "users/current/stats/last_7_days"
    )

    response = SESSION.get(
        url,
        headers={
            "Authorization": f"Bearer {WAKATIME_TOKEN}"
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()["data"]

    total_seconds = data["total_seconds"]
    hours = round(total_seconds / 3600, 1)

    return hours


# --------------------------------------------------
# Fetch Shields.io badge
# --------------------------------------------------

def fetch_shield(message, logo=None, label=""):
    params = {
        "message": str(message),
        "label": label,
        "color": TRANSPARENT,
        "labelColor": TRANSPARENT,
        "style": "flat-square",
    }

    if logo:
        params["logo"] = logo
        params["logoColor"] = BLUE

    response = SESSION.get(
        "https://img.shields.io/static/v1",
        params=params,
        timeout=15,
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)

    # Remove background rectangles
    for element in root.iter():
        tag = element.tag.split("}")[-1]

        if tag == "rect":
            element.set("fill", "none")

    width = float(root.attrib["width"])
    height = float(root.attrib["height"])

    return root, width, height


# --------------------------------------------------
# Generate combined SVG
# --------------------------------------------------

def generate():
    hours = fetch_wakatime()

    shields = []

    # Personal badges
    for name, logo in BADGES:
        shields.append(
            fetch_shield(
                message=name,
                logo=logo,
                label="",
            )
        )

    # WakaTime badge with icon
    shields.append(
        fetch_shield(
            message=f"{hours}h / 7d",
            label="WakaTime",
            logo="wakatime",
        )
    )

    gap = 4
    section_gap = 12

    max_width = max(
        shield[1] for shield in shields
    )

    total_height = (
        sum(shield[2] for shield in shields)
        + gap * (len(shields) - 1)
        + section_gap - gap
    )

    canvas = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "width": str(int(max_width + 0.5)),
            "height": str(int(total_height + 0.5)),
            "viewBox": f"0 0 {max_width} {total_height}",
        },
    )

    y = 0

    for index, (shield, width, height) in enumerate(shields):
        if index == len(BADGES):
            y += section_gap - gap

        shield = copy.deepcopy(shield)

        shield.set("x", "0")
        shield.set("y", str(y))
        shield.set("width", str(width))
        shield.set("height", str(height))

        canvas.append(shield)

        y += height + gap

    # Save SVG
    os.makedirs("img", exist_ok=True)

    output = "img/badge-box.svg"

    tree = ET.ElementTree(canvas)
    tree.write(
        output,
        encoding="utf-8",
        xml_declaration=True,
    )

    print(f"Generated: {output}")
    print(f"WakaTime: {hours}h / 7d")


if __name__ == "__main__":
    generate()
