import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
from gpstrace import makeTrace

load_dotenv()

webhookUrl = os.environ["WEBHOOK"]
launches = 0
landings = 0
embeds = []
files = {}


# if replace returns formatted string
# else returns empty string or param
# builder("hello, {}", "world") -> "hello, world"
# builder("hello, {}", None, empty="no helllo") -> "no hello"
def builder(string: str, replace: str, empty=""):
    if replace:
        return string.format(replace)
    return empty


b = builder


def launchPlane(flight):
    global launches
    generateEmbed("🛫 Start", flight)
    launches += 1


def landPlane(flight):
    global landings
    generateEmbed("🛬 Lądowanie", flight)
    landings += 1


def generateEmbed(event, flight):
    print("making embed", flight.get("aircraft", {}).get("registration"))
    imgId = str(len(files))
    files[imgId] = (f"{imgId}.png", makeTrace(flight.get("trail", [])), "image/png")

    embeds.append(
        {
            "title": f"{event}: {flight.get('aircraft',{}).get('registration')}",
            "description": flight.get("status", {}).get("text", ""),
            "fields": [
                {
                    "name": "🛩️ Model:",
                    "value": flight.get("aircraft", {})
                    .get("model", {})
                    .get("text", "??"),
                    "inline": True,
                },
                {
                    "name": "✈️ Operator",
                    "value": flight.get("airline", {}).get("name", "??"),
                    "inline": True,
                },
                {
                    "name": "ID:",
                    "value": flight.get("identification", {})
                    .get("number", {})
                    .get("default", "??"),
                    "inline": True,
                },
                {
                    "name": "Callsign:",
                    "value": flight.get("identification", {}).get("callsign", "??"),
                    "inline": True,
                },
                {
                    "name": "📍 Position:",
                    "value": f"[{round(flight.get('trail',[])[0].get('lat', '??'),2)}, {round(flight.get('trail',[])[0].get('lng', '??'),2)}](https://osm.org/?mlat={flight.get('trail',[])[0].get('lat', '0')}&mlon={flight.get('trail',[])[0].get('lng', '0')})",
                    "inline": True,
                },
                {
                    "name": "Altitude:",
                    "value": f"{round(flight.get('trail',[])[0].get('alt', 0) * 0.3048)}m",
                    "inline": True,
                },
                {
                    "name": "✈️ From",
                    "value": flight.get("airport", {})
                    .get("origin", {})
                    .get("name", "N/A"),
                    "inline": False,
                },
                {
                    "name": "✈️ To",
                    "value": flight.get("airport", {})
                    .get("destination", {})
                    .get("name", "N/A"),
                    "inline": False,
                },
            ],
            "thumbnail": {
                "url": flight.get("aircraft", {})
                .get("images", {})
                .get("large", {})[0]
                .get(
                    "src", "https://www.jetphotos.com/assets/img/placeholders/large.jpg"
                )
            },
            "url": f"https://www.flightradar24.com/{flight.get('identification', {}).get('callsign')}/{flight.get('identification', {}).get('id')}",
            "color": 16711680,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
            + "Z",
            "image": {"url": f"attachment://{imgId}.png"},
        }
    )


def sendMessage():
    global embeds
    global landings
    global launches
    if len(embeds) == 0:
        return

    payload_json = json.dumps(
        {
            "content": f'{b("🛬 {} Lądowań", landings)}\n{b("🛫 {} Startów", launches)}',
            "tts": False,
            "username": "Plane Spotter",
            "embeds": embeds,
        }
    )

    response = requests.post(
        webhookUrl, files=files, data={"payload_json": payload_json}
    )
    embeds = []
    launches = 0
    landings = 0
