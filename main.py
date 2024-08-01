#!/usr/bin/python3

import requests
from dotenv import load_dotenv
import time
import os
import json
from datetime import datetime

load_dotenv()

webhookUrl = os.environ["WEBHOOK"]
regs = ["HB-LUN", "HB-LUZ", "SP-PRO", "SP-GIS", "SP-FPK", "SP-OPK", "SP-ISS", "SP-OPG"]
url = "https://api.airplanes.live/v2/reg/"
activeFlights = {}


def sendWebhook(message):
    requests.post(webhookUrl, json={"content": message})


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
    sendWebhook("launch: " + json.dumps(activeFlights[hex]))


def landEvent(hex):
    sendWebhook("land: "+ json.dumps(activeFlights[hex]))


def run():
    print(datetime.now().strftime("%H:%M:%S"),"checking...", end="")
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
