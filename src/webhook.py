import requests
import json
from datetime import datetime, timezone
from src.gpstrace import makeTrace
from src.utils import config

webhookUrl = config["webhook"]

# if replace returns formatted string
# else returns empty string or param
# builder("hello, {}", "world") -> "hello, world"
# builder("hello, {}", None, empty="no helllo") -> "no hello"


def builder(string: str, replace, empty=""):
    if replace:
        return string.format(replace)
    return empty


b = builder


def getter(data):
    def get(*path):
        current = data

        for key in path:
            if (isinstance(current, dict) and key in current) or (
                isinstance(current, list)
                and isinstance(key, int)
                and len(current) > key
            ):
                current = current[key]
            else:
                return None

        return current

    return get


class Message:
    delta = 0
    webhookUrl = config["webhook"]
    embeds = []
    skipped = []
    files = []

    def __init__(self, delta):
        self.delta = delta

    def addEmbed(self, flight):
        get = getter(flight)
        flightId = get("identification", "id")
        trace, feedback = makeTrace(flight["track"])

        if trace is None:
            origin = (get("airport", "origin", "name") or "N/A") + b(
                "  (<t:{}:t>)", get("time", "real", "departure"), ""
            )
            destination = (get("airport", "destination", "name") or "N/A") + b(
                "  (<t:{}:t>)", get("time", "real", "arrival"), ""
            )
            self.skipped.append(
                f"[{get('aircraft','identification', 'registration') or '??' }](https://www.flightradar24.com/data/aircraft/{get('identification','callsign')}#{get('identification','id')}) from: {origin} to: {destination}"
            )
            return

        self.files.append(trace)

        self.embeds.append(
            {
                "title": f"✈️ FLight: {get('aircraft','identification', 'registration') or '??' }",
                "description": (get("status", "text") or "") + f"\n{feedback}",
                "fields": [
                    {
                        "name": "🛫 From",
                        "value": (get("airport", "origin", "name") or "N/A")
                        + b("  (<t:{}:t>)", get("time", "real", "departure"), ""),
                        "inline": False,
                    },
                    {
                        "name": "🛬 To",
                        "value": (get("airport", "destination", "name") or "N/A")
                        + b("  (<t:{}:t>)", get("time", "real", "arrival"), ""),
                        "inline": False,
                    },
                ],
                "thumbnail": {
                    "url": get("aircraftImages", "large", 0, "src")
                    or "https://www.jetphotos.com/assets/img/placeholders/large.jpg"
                },
                "url": f"https://www.flightradar24.com/data/aircraft/{get('identification','callsign')}#{get('identification','id')}",
                "color": int(config["embedColor"], base=16),
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
                + "Z",
                "image": {"url": f"attachment://{flightId}.webp"},
            }
        )

    def sendMessage(self):
        # empty
        if len(self.embeds) + len(self.skipped) == 0:
            response = requests.post(
                webhookUrl, data={"content": "No flights today :("}
            )
            response.raise_for_status()

        content = ""

        if self.delta != 0:
            content = f"**This report is based on flight data from {-self.delta} day(s) ago**\n"

        # skipped flights
        if len(self.skipped) > 0:
            content += f"{len(self.skipped)} skipped flights:\n"
            content += "\n".join(self.skipped)

        content += (
            f"\n{len(self.embeds)} flight{'s' if len(self.embeds) > 1 else ''} today:"
        )

        for page in range(0, len(self.embeds), 10):
            self.sendPage(page, content if page == 0 else "")

    def sendPage(self, page: int, content: str):
        print("sending page", page, "with content", content)
