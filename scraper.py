import requests
from datetime import datetime
from bs4 import BeautifulSoup
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

# after: timestamp of last check date
def getFlights(registration:str, day:int):
    flights = []
    res = requests.get(f"https://www.flightradar24.com/data/aircraft/{registration}#", headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    playback_links = soup.find_all('a', title="Show playback of flight")
    for link in playback_links:
        timestamp = int(link.get('data-timestamp'))
        date = datetime.fromtimestamp(timestamp).date()
        if date == day:
            flights.append(link.get('data-flight-hex'))
    return flights

print(getFlights("sp-pro", datetime.now().date()))
