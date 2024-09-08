import json
import os
import requests
import sys
import webhook
import time
from datetime import datetime, timedelta

config = json.load(open("config.json", "r"))



headers = {
    "accept-encoding": "gzip, br",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    "origin": "https://www.flightradar24.com",
    "referer": "https://www.flightradar24.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

bounds = config.get("bounds")
regs = set(config["planes"])
activeFlights = set([])


if os.path.exists("./active.json"):
    activeFlights = set(json.load(open("./active.json", "r")))
else:
    with open("./active.json", "w") as f:
        f.write("[]")


def getData():
    try:
        thisFlights = []
        flights = requests.get(
            f"http://data-cloud.flightradar24.com/zones/fcgi/feed.js?faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&maxage=14400&gliders=1&stats=1&limit=1000&bounds={bounds.replace(',', '%2C')}",
            headers=headers,
        ).json()
        print("\b\b\b\b\b\b\b\b\b\b\b (a/t/e):", len(flights), end="/")
        sys.stdout.flush()
        for flightId in flights:
            flight = flights[flightId]
            if not isinstance(flight, list):
                continue
            if flight[9] in regs:
                thisFlights.append(flightId)
    except Exception as error:
        print("Error getting flights:", error)
        return []
    finally:
        return thisFlights


def sendWebhook():
    webhook.sendMessage()


def launchEvent(hex):
    res = requests.get(
        f"https://data-live.flightradar24.com/clickhandler/?version=1.5&flight={hex}",
        headers=headers,
    ).json()
    print(res.get("aircraft").get("registration"), end="..")
    sys.stdout.flush()
    webhook.launchPlane(res)


def landEvent(hex):
    res = requests.get(
        f"https://data-live.flightradar24.com/clickhandler/?version=1.5&flight={hex}",
        headers=headers,
    ).json()
    print(res.get("aircraft", {}).get("registration"), end="..")
    sys.stdout.flush()
    webhook.landPlane(res)
    activeFlights.remove(hex)


def run():
    start = time.time()
    print(datetime.now().strftime("%H:%M:%S"), "checking...", end="")
    sys.stdout.flush()

    flights = getData()
    print(len(flights), end="/")
    sys.stdout.flush()

    newActive = {}
    queue = []

    for flight in flights:
        newActive[flight] = flight
        if flight not in activeFlights:
            activeFlights.add(flight)
            queue.append((launchEvent, flight))

    for id in list(activeFlights):
        if id not in newActive:
            queue.append((landEvent, id))

    print(len(queue), end=": ")
    for item in queue:
        try:
            print(item[0], item[1])
            item[0](item[1])
        except Exception as error:
            print("\n", error, "\n")

    if len(queue) == 0:
        print("    ", end="")
    else:
        json.dump(list(activeFlights), open("./active.json", "w"))

    print(end="\b\b\b\b sending")
    sys.stdout.flush()

    activeFlights.update(newActive)
    try:
        sendWebhook()
    except Exception as error:
        print("\n", error, "\n")

    diff = round(time.time() - start, 1)

    print("\b\b\b\b\b\b\bdone in", str(diff) + "s!")

    # waiting
    if not config.get("checkHours"):
        return
    now = datetime.now()
    hour = now.hour
    if hour < config["checkHours"][0] or hour > config["checkHours"][1]:
        target = now.replace(
            hour=config["checkHours"][0], minute=0, second=0, microsecond=0
        )
        if target < now:
            target += timedelta(days=1)
        delay = target - now
        print("sleeping for", delay.seconds, "seconds")
        time.sleep(delay.seconds)

    if not config.get("checkDays"):
        return
    now = datetime.now()
    day = now.weekday()
    if day not in config["checkDays"]:
        delay = (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)) - now
        print("sleeping for", delay.seconds, "seconds")
        time.sleep(delay.seconds)



def start():
    while True:
        try:
            run()
        except Exception as error:
            print("\n", error, "\n")
        time.sleep(config.get("interval", 60))