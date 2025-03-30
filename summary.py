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
    date = datetime.now().strftime(r"%d %m, %H:%M:%S")
    flights = []
    sys.stdout.flush()
    for index, registration in enumerate(config["planes"]):
        flights.extend(scraper.getFlights(registration.lower(),
                       datetime.now().date() + timedelta(days=delta)))
        print(
            f"\r[{date}] checking {index+1} of {len(config['planes'])}: {registration} ({round((index+1) / len(config['planes']) * 100)}%)",
            end="",
        )
        sys.stdout.flush()
        time.sleep(5)  # ratelimit
    print()
    print(f"got {len(flights)} flights", end="")
    sys.stdout.flush()

    for flight in flights:
        res = requests.get(
            f"https://data-live.flightradar24.com/clickhandler/?version=1.5&flight={flight}",
            headers=headers,
        )
        res.raise_for_status()
        webhook.generateEmbed("✈️ FLight", res.json())
    webhook.sendMessage()
    print()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        delta = 0
    else:
        delta = int(sys.argv[1])
    _run(delta=delta)
