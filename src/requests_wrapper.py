import requests
import json
import os
import time

from src.utils import config

url = config["flareSolver"]
headers = {"Content-Type": "application/json"}

lock = 0


def get(targetUrl: str) -> str:
    global lock

    fileName = "./dump/" + urlToFilename(targetUrl)
    dump = shouldDump(targetUrl)
    if dump and os.path.exists(fileName):
        return open(fileName, "r").read()
    payload = {"cmd": "request.get", "url": targetUrl, "maxTimeout": 60000}
    time.sleep(max(0, lock - time.time()))
    response = requests.post(url, headers=headers, json=payload)
    lock = time.time() + 5
    data = response.json()
    text = data["solution"]["response"]

    if dump:
        open(fileName, "w").write(text)

    return text


def toJson(data: str):
    data = data.removeprefix(
        '<html><head><meta name="color-scheme" content="light dark"><meta charset="utf-8"></head><body><pre>'
    )
    data = data.removesuffix(
        '</pre><div class="json-formatter-container"></div></body></html>'
    )
    return json.loads(data)


def urlToFilename(url: str) -> str:
    encoded = url.removeprefix("https://").replace("/", "_")
    return encoded


def shouldDump(url: str) -> bool:
    DUMP = config.get("dump")
    if DUMP == "ALL":
        return True
    elif "FLIGHT" in DUMP and url.startswith(
        "https://api.flightradar24.com/common/v1/flight-playback.json"
    ):
        return True
    elif "TILE" in DUMP and url.startswith("https://osm.rrze.fau.de/osmhd"):
        return True
    return False
