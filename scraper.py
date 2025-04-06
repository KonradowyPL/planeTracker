import requests
from datetime import datetime
from bs4 import BeautifulSoup
from utils import headers


def getFlights(registration: str, day):
    flights = []
    res = requests.get(
        f"https://www.flightradar24.com/data/aircraft/{registration}#", headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, "html.parser")
    playback_links = soup.find_all('a', title="Show playback of flight")
    for link in playback_links:
        timestamp = int(link.get('data-timestamp'))
        date = datetime.fromtimestamp(timestamp).date()
        if date == day:
            flights.append(link.get('data-flight-hex'))
    return flights[::-1]
