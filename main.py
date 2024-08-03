#!/usr/bin/python3

import requests

import time

from datetime import datetime
import webhook



regs = ["HB-LUN", "HB-LUZ", "SP-PRO", "SP-GIS", "SP-FPK", "SP-OPK", "SP-ISS", "SP-OPG"]
url = "https://api.airplanes.live/v2/reg/"
activeFlights = {}


def getData():
    return  {
  "ac": [
    {
      "hex": "4b1f2d",
      "type": "mode_s",
      "flight": "SFS60   ",
      "r": "HB-LUZ",
      "t": "P68",
      "desc": "PARTENAVIA P-68 Observer",
      "ownOp": "Swiss Flight Services Sa",
      "year": "2012",
      "alt_baro": 6150,
      "gs": 146.0,
      "ias": 133,
      "tas": 148,
      "mach": 0.224,
      "track": 24.96,
      "roll": -0.53,
      "mag_heading": 12.48,
      "true_heading": 8.56,
      "baro_rate": -64,
      "squawk": "7000",
      "nav_qnh": 1016.0,
      "nav_altitude_mcp": 6208,
      "rr_lat": 49.7,
      "rr_lon": 16.4,
      "alert": 0,
      "spi": 0,
      "mlat": [],
      "tisb": [],
      "messages": 11514,
      "seen": 4.4,
      "rssi": -9.5
    },
    {
      "hex": "4895e9",
      "type": "mode_s",
      "flight": "SPFPK   ",
      "r": "SP-FPK",
      "t": "PA31",
      "desc": "PIPER PA-31-300/310/325/350/425",
      "ownOp": "Regional Air Services",
      "alt_baro": 13900,
      "squawk": "3654",
      "emergency": "none",
      "category": "A1",
      "rr_lat": 47.5,
      "rr_lon": 16.7,
      "nic_baro": 0,
      "nac_p": 0,
      "sil": 1,
      "sil_type": "perhour",
      "gva": 0,
      "sda": 2,
      "alert": 0,
      "spi": 0,
      "mlat": [],
      "tisb": [],
      "messages": 7250,
      "seen": 0.9,
      "rssi": -21.8
    }
  ],
  "msg": "No error",
  "now": 1722416383040,
  "total": 2,
  "ctime": 1722416383040,
  "ptime": 0
}
    try:
        response = requests.get(url + ",".join(regs))
        if response.status_code != 200:
            raise (response.status_code, response.text())
    except:  # noqa: E722
        return {}
    finally:
        return response.json()

def sendWebhook():
    webhook.sendMessage()

def launchEvent(hex):
    webhook.launchPlane(activeFlights[hex])

def landEvent(hex):
    webhook.landPlane(activeFlights[hex])


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
    sendWebhook()


def main():
    while True:
        run()
        time.sleep(60)


if __name__ == "__main__":
    main()
