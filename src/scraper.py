import src.requests_wrapper as requests_wrapper
from datetime import datetime
from bs4 import BeautifulSoup


def getFlights(registration: str, day):
    flights = []
    content = requests_wrapper.get(
        f"https://www.flightradar24.com/data/aircraft/{registration}"
    )
    soup = BeautifulSoup(content, "html.parser")
    playback_links = soup.find_all("a", title="Show playback of flight")
    for link in playback_links:
        timestamp = int(link.get("data-timestamp", ""))
        date = datetime.fromtimestamp(timestamp).date()
        if date == day or True:
            flights.append(link.get("data-flight-hex"))
    return flights[::-1]
