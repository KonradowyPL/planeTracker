import src.scraper as scraper
from datetime import datetime, timedelta
import src.requests_wrapper as requests_wrapper
import sys
import src.webhook as webhook
import time
from src.utils import config


def run(delta=0):
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
            time.sleep(5)  # ratelimit
    print(f"got {len(flights)} flights")

    for index, flight in enumerate(flights):

        print(f"Generating map ({index + 1} of {len(flights)})   \r", end="")
        print("map", flight)

        sys.stdout.flush()

        res = requests_wrapper.get(
            f"https://api.flightradar24.com/common/v1/flight-playback.json?flightId={flight}",
        )

        webhook.generateEmbed(
            "✈️ FLight",
            requests_wrapper.toJson(res)["result"]["response"]["data"]["flight"],
        )
    webhook.delta = delta
    webhook.sendMessage()
    print()
