import webhook
from FlightRadar24 import FlightRadar24API


fr_api = FlightRadar24API()

regs = {"HB-LUN", "HB-LUZ", "SP-PRO", "SP-GIS", "SP-FPK", "SP-OPK", "SP-ISS", "SP-OPG", "PH-BVW"}
activeFlights = {}


def getData():
    try:
        thisFlights = []
        flights = fr_api.get_flights()
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
    # while True:
        run()
        # time.sleep(60)


if __name__ == "__main__":
    main()
