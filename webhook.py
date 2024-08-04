import requests
import os
import json
from images import getImage
from dotenv import load_dotenv
from datetime import datetime

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
            "title": f"{event}: {flight.get('r')}",
            "description": f"{b('**{}**', flight.get('desc'))}{b(newLine + '{}', flight.get('ownOp'))}{b(newLine + '{}', flight.get('flight'))}",
            "fields": [
                {
                    "name": "✈️ Śledź:",
                    "value": "~~[Flightradar](https://google.com)~~\n~~[Airplanes.live](https://google.com)~~",
                    "inline": True,
                },
                {
                    "name": "📍 Pozycja:",
                    "value": f"{flight.get('rr_lat','??')}, {flight.get('rr_lon', '??')}\n[OSM](https://osm.org/?mlat={flight.get('rr_lat','0')}&mlon={flight.get('rr_lon','0')})",
                    "inline": True,
                },
            ],
            "thumbnail": {"url": getImage(flight.get("r", ""))},
            "url": f'https://www.flightradar24.com/data/aircraft/{flight.get("r")}',
            "color": 16711680,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
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
            # "content": "-# 🛬 5 Lądowań\n-# 🛫 3 Startów",
            "content": f'{b("🛬 {} Lądowań", landings)}\n{b("🛫 {} Startów", launches)}',
            "tts": False,
            "username": "Plane Spotter",
            "embeds": embeds,
        },
    )
    embeds = []
    launches = 0
    landings = 0
