#!/usr/bin/python3

import requests
import time

regs = ["HB-LUN", "HB-LUZ", "SP-PRO", "SP-GIS", "SP-FPK", "SP-OPK", "SP-ISS", "SP-OPG"]
url = "https://api.airplanes.live/v2/reg/"
activeFlights = {}



def getData():
    try:
        response = requests.get(url + ",".join(regs))
        if response.status_code != 200:
            raise (response.status_code, response.text())
    except:  # noqa: E722
        return {}    
    finally:
        return response.json()


def launchEvent(hex):
    print("launch:", hex, activeFlights[hex])


def landEvent(hex):
    print("land:", hex, activeFlights[hex])


def run():
    print("checking...", end="")
    data = getData()
    if "ac" not in data:
        return print("   Error!")
    print("   Done!")

    newActive = {}

    for flight in data["ac"]:
        hex = flight["hex"]
        newActive[hex] = flight
        if hex not in activeFlights:
            activeFlights[hex] = flight
            launchEvent(hex)

    for hex in list(activeFlights):
        if hex not in newActive:
            landEvent(hex)
            del activeFlights[hex]

    activeFlights.update(newActive)


def main():
    while True:
        run()
        time.sleep(60)

if __name__ == "__main__":
    main()