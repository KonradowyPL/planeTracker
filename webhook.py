import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

webhookUrl = os.environ["WEBHOOK"]
launches = 0
landings = 0
embeds = []

newLine = "\n"  # python does not allow '\' char within f strings


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
    embeds.append(
        {
            "title": f"{event}: {flight.get('aircraft',{}).get('registration')}",
            "description": "",
            "fields": [
                {
                    "name": "🛩️ Model:",
                    "value": flight.get("aircraft", {})
                    .get("model", {})
                    .get("text", "??"),
                    "inline": True,
                },
                {
                    "name": "Callsign:",
                    "value": flight.get("identification", {}).get("callsign", "??"),
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
                    "name": "✈️ Operator",
                    "value": flight.get("airline", {}).get("name", "??"),
                    "inline": True,
                },
                {
                    "name": "📍 Pozycja:",
                    "value": f"[{flight.get('trail',[])[0].get('lat', '??')}, {flight.get('trail',[])[0].get('lng', '??')}](https://osm.org/?mlat={flight.get('trail',[])[0].get('lat', '0')}&mlon={flight.get('trail',[])[0].get('lng', '0')})",
                    "inline": True,
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
        }
    )


def sendMessage():
    global embeds
    global landings
    global launches
    if len(embeds) == 0:
        return

    requests.post(
        webhookUrl,
        json={
            "content": f'{b("🛬 {} Lądowań", landings)}\n{b("🛫 {} Startów", launches)}',
            "tts": False,
            "username": "Plane Spotter",
            "embeds": embeds,
        },
    )
    embeds = []
    launches = 0
    landings = 0
