#!/usr/bin/python3
import scraper
from datetime import datetime, timedelta
import requests
import sys
import webhook
import time
import traceback
from utils import config, headers


def run():
    try:
        _run()
    except Exception:
        traceback.print_exc()


def _run(delta=0):
    webhook.clear()
    date = datetime.now().date() + timedelta(days=delta)
    flights = []
    for index, registration in enumerate(config["planes"]):
        print(
            f"[{index+1} / {len(config['planes'])}] {registration}",
            end="",
        )
        sys.stdout.flush()

        current = scraper.getFlights(registration.lower(),
                                     date)
        flights.extend(current)
        print(f": {len(current)}")

        if (index+1 != len(config['planes'])):
            time.sleep(5)  # ratelimit
    print(f"got {len(flights)} flights")

    for index, flight in enumerate(flights):

        print(f"Generating map ({index + 1} of {len(flights)})   \r", end="")
        sys.stdout.flush()

        res = requests.get(
            f"https://data-live.flightradar24.com/clickhandler/?version=1.5&flight={flight}",
            headers=headers,
        )
        res.raise_for_status()
        webhook.generateEmbed("✈️ FLight", res.json())
    webhook.delta = delta
    webhook.sendMessage()
    print()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        delta = 0
    else:
        delta = int(sys.argv[1])
    _run(delta=delta)
