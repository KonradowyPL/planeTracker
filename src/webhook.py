import requests
import json
from datetime import datetime, timezone
from src.gpstrace import makeTrace
from src.utils import config

delta = 0

webhookUrl = config["webhook"]
launches = 0
landings = 0
embeds = []
skipped = []
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

    imgId = get("identification", 'id') or str(len(files))
    trace = makeTrace(flight.get("trail", []))
    if trace:
        files[imgId] = (
            f"{imgId}.webp",
            trace,
            "image/webp",
        )
    else:
        _from = (get("airport", "origin", "name") or "N/A") + \
            b("  (<t:{}:t>)", get("time", "real", "departure"), "")
        to = (get("airport", "destination", "name") or "N/A") + \
            b("  (<t:{}:t>)", get("time", "real", "arrival"), "")
        addSkipped(
            f"[{get('aircraft', 'registration') or '??' }](https://www.flightradar24.com/data/aircraft/{get('identification','callsign')}#{get('identification','id')}) from: {_from} to: {to}")
        return

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
                # {
                #     "name": "📍 Position:",
                #     "value": f"[{round(get('trail',0,'lat') or 0, 2) or '??'}, {round(get('trail',0,'lng') or 0, 2) or '??'}](https://osm.org/?mlat={get('trail',0,'lat') or 0}&mlon={get('trail',0,'lng') or 0})",
                #     "inline": True,
                # },
                # {
                #     "name": "Altitude:",
                #     "value": f"{round((get('trail', 0, 'alt') or 0) * 0.3048)}m",
                #     "inline": True,
                # },
                {
                    "name": "🛫 From",
                    "value": (get("airport", "origin", "name") or "N/A") + b("  (<t:{}:t>)", get("time", "real", "departure"), ""),
                    "inline": False,
                },
                {
                    "name": "🛬 To",
                    "value": (get("airport", "destination", "name") or "N/A") + b("  (<t:{}:t>)", get("time", "real", "arrival"), ""),
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


def addSkipped(text):
    global skipped
    skipped.append(text)


def sendMessage():
    global embeds
    global landings
    global launches
    global skipped
    global files

    if len(embeds) + len(skipped) == 0:
        return requests.post(webhookUrl, data={'content': "No flights today :("})

    message = ""

    if delta != 0:
        message = f"**This report is based on flight data from {-delta} day(s) ago**\n"

    if len(skipped) > 0:
        message += f"{len(skipped)} skipped flights.\n"
        message += "\n".join(skipped)

    if len(embeds) == 0:
        payload_json = json.dumps(
            {
                "content": message,
                "tts": False,
                "username": config.get("name"),
                "icon": config.get("icon"),
            }
        )

        response = requests.post(
            webhookUrl, data={
                "payload_json": payload_json}
        )
        response.raise_for_status()
        clear()
        return

    message += f"\n{len(embeds)} flight{'s' if len(embeds) > 1 else ''} today:"

    for index in range(0, len(embeds), 10):
        msgEmbeds = embeds[index:(index+10)]
        embed_img_ids = set(embed['image']['url'].split(
            'attachment://')[1].replace('.webp', '') for embed in msgEmbeds)
        filtered_files = {imgId: file_data for imgId,
                          file_data in files.items() if imgId in embed_img_ids}

        payload_json = json.dumps(
            {
                "content": message,
                "tts": False,
                "username": config.get("name"),
                "embeds": msgEmbeds,
                "icon": config.get("icon"),
            }
        )

        message = ""

        response = requests.post(
            webhookUrl, files=filtered_files, data={
                "payload_json": payload_json}
        )

        response.raise_for_status()

        print("\n", response.text)

    clear()


def clear():
    global embeds
    global landings
    global launches
    global files
    embeds = []
    files = {}
    skipped = []
    launches = 0
    landings = 0
