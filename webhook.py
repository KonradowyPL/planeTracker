import requests
import os
import json
from images import getImage
from dotenv import load_dotenv

load_dotenv()

webhookUrl = os.environ["WEBHOOK"]
launches = 0
landings = 0
embeds = []


def launchPlane(flight):
    generateEmbed("🛫 Start", flight)


def landPlane(flight):
    generateEmbed("🛬 Lądowanie", flight)


def generateEmbed(event, flight):
    embeds.append(
        {
            "title": f"{event}: {flight.get('r')}",
            "description": f"**{flight.get('desc', '')}**\n{flight.get('ownOp', '')}\n{flight.get('flight', '')}",
            "fields": [
                {
                    "name": "✈️ Śledź:",
                    "value": "[Flightradar]()\n[Airplanes.live]() ",
                    "inline": True,
                },
                {
                    "name": "📍 Pozycja:",
                    "value": f"{flight.get('rr_lat')}, {flight.get('rr_lon')}\n[OSM]()",
                    "inline": True,
                },
            ],
            "thumbnail": {
                "url": getImage(flight.get('r', "SP-FPK"))
            },
            "url": "https://google.com",
            "color": 16711680,
            "timestamp": "2024-08-06T22:00:00.000Z",
        }
    )


def sendMessage():
    global embeds
    if (len(embeds) == 0):
        return

    requests.post(
        webhookUrl,
        json={
            "content": "-# 🛬 5 Lądowań\n-# 🛫 3 Startów",
            "tts": False,
            "username": "Plane Spotter",
            "embeds": embeds,
        },
    )
    embeds = []
