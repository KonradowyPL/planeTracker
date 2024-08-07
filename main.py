import webhook
from FlightRadar24 import FlightRadar24API, FlightTrackerConfig
import time
import base64

fr_api = FlightRadar24API()
fr_api.set_flight_tracker_config(
    FlightTrackerConfig(vehicles="0", gliders="0", limit="10000")
)


bounds = "72.57,33.57,-16.96,53.05"  # europe
regs = {
    "HB-LUN",
    "HB-LUZ",
    "SP-PRO",
    "SP-GIS",
    "SP-FPK",
    "SP-OPK",
    "SP-ISS",
    "SP-OPG",
    "OH-LZT",
}
activeFlights = {}


def getData():
    try:
        thisFlights = []
        flights = fr_api.get_flights(bounds=bounds)
        print(len(flights))
        for flight in flights:
            if flight.registration in regs:
                thisFlights.append(flight)
    except Exception as error:
        print("Error getting flights: ", error)
        return []
    finally:
        return thisFlights


def sendWebhook():
    webhook.sendMessage()


def launchEvent(hex):
    webhook.launchPlane(fr_api.get_flight_details(activeFlights[hex]))


def landEvent(hex):
    webhook.landPlane(fr_api.get_flight_details(activeFlights[hex]))


def run():
    print("checking...")
    flights = getData()
    newActive = {}

    for flight in flights:
        newActive[flight.id] = flight
        if flight.id not in activeFlights:
            activeFlights[flight.id] = flight
            launchEvent(flight.id)

    for id in list(activeFlights):
        if id not in newActive:
            landEvent(id)
            del activeFlights[id]

    activeFlights.update(newActive)
    sendWebhook()
    print("done!")


def main():
    while True:
        run()
        time.sleep(60)


if __name__ == "__main__":
    main()
