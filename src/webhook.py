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
        nonlocal data

        for key in path:
            if (isinstance(data, dict) and key in data) or (
                isinstance(data, list) and isinstance(key, int) and len(data) > key
            ):
                data = data[key]
            else:
                return None
        return data

    return get


class Message:
    delta = 0
    webhookUrl = config["webhook"]
    launches = 0
    landings = 0
    embeds = []
    skipped = []
    files = {}

    def __init__(self, delta):
        self.delta = delta

    def addSkipped(self, text):
        self.skipped.append(text)

    def addEmbed(self, flight):
        get = getter(flight)
        flightId = get("identification", "id")
        trace, feedback = makeTrace(flight["track"])

        if trace is None:
            _from = (get("airport", "origin", "name") or "N/A") + b(
                "  (<t:{}:t>)", get("time", "real", "departure"), ""
            )
            to = (get("airport", "destination", "name") or "N/A") + b(
                "  (<t:{}:t>)", get("time", "real", "arrival"), ""
            )
            self.addSkipped(
                f"[{get('aircraft','identification', 'registration') or '??' }](https://www.flightradar24.com/data/aircraft/{get('identification','callsign')}#{get('identification','id')}) from: {_from} to: {to}"
            )
            return

        self.files[flightId] = (
            f"{flightId}.webp",
            trace,
            "image/webp",
        )
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
        if len(self.embeds) + len(self.skipped) == 0:
            return requests.post(webhookUrl, data={"content": "No flights today :("})

        message = ""

        if self.delta != 0:
            message = f"**This report is based on flight data from {-self.delta} day(s) ago**\n"

        if len(self.skipped) > 0:
            message += f"{len(self.skipped)} self.skipped flights.\n"
            message += "\n".join(self.skipped)

        if len(self.embeds) == 0:
            payload_json = json.dumps(
                {
                    "content": message,
                    "tts": False,
                    "username": config.get("name"),
                    "icon": config.get("icon"),
                }
            )

            response = requests.post(webhookUrl, data={"payload_json": payload_json})
            response.raise_for_status()
            return

        message += (
            f"\n{len(self.embeds)} flight{'s' if len(self.embeds) > 1 else ''} today:"
        )

        for index in range(0, len(self.embeds), 10):
            msgembeds = self.embeds[index : (index + 10)]
            embed_img_ids = set(
                embed["image"]["url"].split("attachment://")[1].replace(".webp", "")
                for embed in msgembeds
            )
            filtered_files = {
                imgId: file_data
                for imgId, file_data in self.files.items()
                if imgId in embed_img_ids
            }

            print(
                "message with:",
                len(msgembeds),
                "self.embeds,",
                len(filtered_files),
                "files",
            )

            payload_json = json.dumps(
                {
                    "content": message[:1999],
                    "tts": False,
                    "username": config.get("name"),
                    "embeds": msgembeds,
                    "icon": config.get("icon"),
                }
            )

            message = ""

            response = requests.post(
                webhookUrl, files=filtered_files, data={"payload_json": payload_json}
            )

            response.raise_for_status()

            print("\n", response.text)
