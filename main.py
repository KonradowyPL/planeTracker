import webhook
from FlightRadar24 import FlightRadar24API, FlightTrackerConfig
import time
import sys
from datetime import datetime, timezone

fr_api = FlightRadar24API()
fr_api.set_flight_tracker_config(
    FlightTrackerConfig(vehicles="0", gliders="0", limit="10000")
)


bounds = "56.86,48.22,11.06,28.26"  # poland
regs = {
    "HB-LUN",
    "HB-LUZ",
    "SP-PRO",
    "SP-GIS",
    "SP-FPK",
    "SP-OPK",
    "SP-ISS",
    "SP-OPG",
    "OY-JZN",
}
activeFlights = {}


def getData():
    try:
        thisFlights = []
        flights = fr_api.get_flights(bounds=bounds)
        print("\b\b\b\b\b\b\b\b\b\b\bflights:", len(flights), end=" ")
        sys.stdout.flush()
        for flight in flights:
            if flight.registration in regs:
                thisFlights.append(flight)
    except Exception as error:
        print("\rError getting flights:", error)
        return []
    finally:
        return thisFlights


def sendWebhook():
    webhook.sendMessage()


def launchEvent(hex):
    print(activeFlights[hex].registration, end=".")
    sys.stdout.flush()
    res = fr_api.get_flight_details(activeFlights[hex])
    print(end=".")
    sys.stdout.flush()
    webhook.launchPlane(res)


def landEvent(hex):
    print(activeFlights[hex].registration, end=".")
    sys.stdout.flush()
    res = fr_api.get_flight_details(activeFlights[hex])
    print(end=".")
    sys.stdout.flush()
    webhook.landPlane(res)
    del activeFlights[id]


def run():
    print(datetime.now(timezone.utc).strftime("%H:%M:%S"), "checking...", end="")
    sys.stdout.flush()

    flights = getData()
    print("tracked:", len(flights), end=" ")
    sys.stdout.flush()

    newActive = {}
    queue = []

    for flight in flights:
        newActive[flight.id] = flight
        if flight.id not in activeFlights:
            activeFlights[flight.id] = flight
            queue.append((launchEvent, flight.id))

    for id in list(activeFlights):
        if id not in newActive:
            queue.append((landEvent, id))

    print("events:", len(queue), end=": ")
    for item in queue:
        item[0](item[1])

    if len(queue) == 0:
        print("    ", end="")

    print(end="\b\b\b\b sending")
    sys.stdout.flush()

    activeFlights.update(newActive)
    sendWebhook()
    print("\b\b\b\b\b\b\bdone!  ")


def main():
    while True:
        run()
        time.sleep(60)


if __name__ == "__main__":
    main()
