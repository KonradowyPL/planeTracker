#!/usr/bin/python3
import src.scraper as scraper
from datetime import datetime, timedelta
import src.requests_wrapper as requests_wrapper
import sys
import src.webhook as webhook
import time
import traceback
from src.utils import config


def run():
    try:
        _run()
    except Exception:
        traceback.print_exc()


def _run(delta=0):
    date = datetime.now().date() + timedelta(days=delta)
    flights = []
    for index, registration in enumerate(config["planes"]):
        print(
            f"[{index+1} / {len(config['planes'])}] {registration}",
            end="",
        )
        sys.stdout.flush()

        current = scraper.getFlights(registration.lower(), date)
        flights.extend(current)
        print(f": {len(current)}")

        if index + 1 != len(config["planes"]):
            # time.sleep(5)  # ratelimit
            time.sleep(0)  # ratelimit
    print(f"got {len(flights)} flights")

    for index, flight in enumerate(flights):

        print(f"Generating map ({index + 1} of {len(flights)})   \r", end="")
        print("map", flight)
        
        sys.stdout.flush()

        res = requests_wrapper.get(
            f"https://api.flightradar24.com/common/v1/flight-playback.json?flightId={flight}",
        )

        webhook.generateEmbed("✈️ FLight", requests_wrapper.toJson(res)['result']['response']['data']['flight'])
    webhook.delta = delta
    webhook.sendMessage()
    print()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        delta = 0
    else:
        delta = int(sys.argv[1])
    _run(delta=delta)
