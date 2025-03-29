import requests
import json
from datetime import datetime, timezone
from gpstrace import makeTrace
from utils import config, headers
import sys


webhookUrl = config["webhook"]
launches = 0
landings = 0
embeds = []
files = {}


# if replace returns formatted string
# else returns empty string or param
# builder("hello, {}", "world") -> "hello, world"
# builder("hello, {}", None, empty="no helllo") -> "no hello"
def builder(string: str, replace, empty=""):
    if replace:
        return string.format(replace)
    return empty


b = builder

def generateEmbed(event, flight):
    def get(*path):
        dat = flight
        for key in path:
            if (isinstance(dat, dict) and key in dat) or (
                isinstance(dat, list) and isinstance(
                    key, int) and len(dat) > key
            ):
                dat = dat[key]
            else:
                return None
        return dat

    imgId = str(len(files))
    trace = makeTrace(flight.get("trail", []))
    print(end=".")
    sys.stdout.flush()
    if trace:
        files[imgId] = (
            f"{imgId}.webp",
            trace,
            "image/webp",
        )

    embeds.append(
        {
            "title": f"{event}: {get('aircraft', 'registration') or '??' }",
            "description": get("status", "text") or "",
            "fields": [
                {
                    "name": "🛩️ Model:",
                    "value": get("aircraft", "model", "text") or "??",
                    "inline": True,
                },
                {
                    "name": "✈️ Operator",
                    "value": get("airline", "name") or "??",
                    "inline": True,
                },
                *({
                    "name": "ID:",
                    "value": get("identification", "number", "default") or "??",
                    "inline": True,
                } if get("identification", "number", "default") else {}),
                {
                    "name": "Callsign:",
                    "value": get("identification", "callsign") or "??",
                    "inline": True,
                },
                {
                    "name": "📍 Position:",
                    "value": f"[{round(get('trail',0,'lat') or 0, 2) or '??'}, {round(get('trail',0,'lng') or 0, 2) or '??'}](https://osm.org/?mlat={get('trail',0,'lat') or 0}&mlon={get('trail',0,'lng') or 0})",
                    "inline": True,
                },
                {
                    "name": "Altitude:",
                    "value": f"{round((get('trail', 0, 'alt') or 0) * 0.3048)}m",
                    "inline": True,
                },
                {
                    "name": "✈️ From",
                    "value": get("airport", "origin", "name") or "N/A",
                    "inline": False,
                },
                {
                    "name": "✈️ To",
                    "value": get("airport", "destination", "name") or "N/A",
                    "inline": False,
                },
            ],
            "thumbnail": {
                "url": get("aircraft", "images", "large", 0, "src")
                or "https://www.jetphotos.com/assets/img/placeholders/large.jpg"
            },
            "url": f"https://www.flightradar24.com/data/aircraft/{get('identification','callsign')}#{get('identification','id')}",
            "color": int(config["embedColor"], base=16),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
            + "Z",
            "image": {"url": f"attachment://{imgId}.webp"},
        }
    )
    print(end=".")
    sys.stdout.flush()


def sendMessage():
    global embeds
    global landings
    global launches
    global files

    mode = config['mode']

    if len(embeds) == 0:
        if mode != "summary":
            return  # live mode
        return requests.post(webhookUrl, data={'content': "No flights today :("})

    if mode == "live":
        message = f'{b("🛬 {} Landings", landings)}\n{b("🛫 {} Launches", launches)}',
    else:
        message = f"{len(embeds)} flights today:"

    payload_json = json.dumps(
        {
            "content": message,
            "tts": False,
            "username": config.get("name"),
            "embeds": embeds,
            "icon": config.get("icon"),
        }
    )

    response = requests.post(
        webhookUrl, files=files, data={"payload_json": payload_json}
    )
    if response.status_code != 200:
        print("\n", response.text)

    clear()


def clear():
    global embeds
    global landings
    global launches
    global files
    embeds = []
    files = {}
    launches = 0
    landings = 0
