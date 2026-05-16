import json
import requests
from io import BytesIO
from datetime import datetime, timezone

from src.utils import config
from src.gpstrace import makeTrace


# if replace returns formatted string
# else returns empty string or param
# builder("hello, {}", "world") -> "hello, world"
# builder("hello, {}", None, empty="no helllo") -> "no hello"
def builder(string: str, replace, empty=""):
    if replace:
        return string.format(replace)
    return empty


b = builder
webhookUrl = config["webhook"]
baseRequest = {
    "tts": False,
    "username": config.get("name"),
    "icon": config.get("icon"),
}


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

    skipped: list[str] = []
    data: list[tuple[str, dict, BytesIO]] = []

    def __init__(self, delta):
        self.delta = delta

    def addEmbed(self, flight):
        get = getter(flight)
        flightId = get("identification", "id")
        assert type(flightId) == str

        trace, feedback = makeTrace(flight["track"])
        departure = get("track", 0, "timestamp")
        arrival = get("track", -1, "timestamp")
        link = f"https://www.flightradar24.com/data/aircraft/{get('identification','callsign')}#{get('identification','id')}"
        if trace is None:
            origin = (get("airport", "origin", "name") or "N/A") + b(
                "  (<t:{}:t>)", departure, ""
            )
            destination = (get("airport", "destination", "name") or "N/A") + b(
                "  (<t:{}:t>)", arrival, ""
            )
            self.skipped.append(
                f"[{get('aircraft','identification', 'registration') or '??' }]({link}) from: {origin} to: {destination}"
            )
            return

        embed = {
            "title": f"✈️ FLight: {get('aircraft','identification', 'registration') or '??' }",
            "description": (get("status", "text") or "") + f"\n{feedback}",
            "fields": [
                {
                    "name": "🛫 From",
                    "value": (get("airport", "origin", "name") or "N/A")
                    + b("  (<t:{}:t>)", departure, ""),
                    "inline": False,
                },
                {
                    "name": "🛬 To",
                    "value": (get("airport", "destination", "name") or "N/A")
                    + b("  (<t:{}:t>)", arrival, ""),
                    "inline": False,
                },
            ],
            "thumbnail": {
                "url": get("aircraftImages", "large", 0, "src")
                or "https://www.jetphotos.com/assets/img/placeholders/large.jpg"
            },
            "url": link,
            "color": int(config["embedColor"], base=16),
            "timestamp": datetime.fromtimestamp(arrival or 0, timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "image": {"url": f"attachment://{flightId}.webp"},
        }
        self.data.append(
            (
                flightId,
                embed,
                trace,
            )
        )

    def sendMessage(self):
        # empty
        if len(self.data) + len(self.skipped) == 0:
            response = requests.post(
                webhookUrl, data={"content": "No flights today :(", **baseRequest}
            )
            response.raise_for_status()

        content = ""

        if self.delta != 0:
            content = f"**This report is based on flight data from {-self.delta} day(s) ago**\n"

        # skipped flights
        if len(self.skipped) > 0:
            content += f"{len(self.skipped)} skipped flights:\n"
            content += "\n".join(self.skipped)

        if len(self.data) == 0 and len(self.skipped) > 0:
            self.sendPage(0, content)
            return
        
        content += (
            f"\n{len(self.data)} flight{'s' if len(self.data) > 1 else ''} today:"
        )

        for page in range(0, len(self.data), 10):
            self.sendPage(page, content if page == 0 else "")

    def sendPage(self, page: int, content: str):
        data = self.data[page : page + 10]
        embeds = [embed for _, embed, _ in data]

        files = {
            flightId: (f"{flightId}.webp", buffer, "image/webp")
            for flightId, _, buffer in data
        }

        payload = {"content": content, "embeds": embeds}
        response = requests.post(
            webhookUrl,
            files=files,
            data={"payload_json": json.dumps(payload), **baseRequest},
        )
        response.raise_for_status()
