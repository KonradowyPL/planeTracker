import json
import scraper
from datetime import datetime
import requests
import sys
import webhook
import time
import schedule

config = json.load(open("config.json", "r"))

headers = {
    "accept-encoding": "gzip, br",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    "origin": "https://www.flightradar24.com",
    "referer": "https://www.flightradar24.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}


def start():
    run()
    while True:
        schedule.every().day.at("23:00").do(run)
        time.sleep(3600)

def run():
    flights = []
    print("checking", end="")
    sys.stdout.flush()
    for index, registration in enumerate(config['planes']):
        flights.extend(scraper.getFlights(registration.lower(), datetime.now().date()))
        print(f"\rchecking {index} of {len(config['planes'])}: {registration} ({round(index / len(config['planes']) * 100)}%)", end="")
        sys.stdout.flush()
        time.sleep(5) # ratelimit
    print()
    print(f"got {len(flights)} flights", end="")
    sys.stdout.flush()
    
    for flight in flights:
        res = requests.get(
            f"https://data-live.flightradar24.com/clickhandler/?version=1.5&flight={flight}",
            headers=headers,
        )
        res.raise_for_status()
        webhook.generateEmbed("✈️ FLight",res.json())
    webhook.sendMessage()
    if len(flights) == 0:
        print()
    

