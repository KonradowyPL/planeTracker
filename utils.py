import json

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

# color values from
# https://support.fr24.com/support/solutions/articles/3000115027-why-does-the-aircraft-s-trail-change-colour
colors = {
    13000: "#ff0000",
    12500: "#ff00e4",
    12000: "#d800ff",
    11500: "#ae00ff",
    11000: "#9600ff",
    10500: "#7800ff",
    10000: "#6000ff",
    9500: "#4e00ff",
    9000: "#3600ff",
    8500: "#2400ff",
    8000: "#1200ff",
    7500: "#0000ff",
    7000: "#001eff",
    6500: "#0030ff",
    6000: "#0054ff",
    5500: "#0078ff",
    5000: "#0096ff",
    4500: "#00a8ff",
    4000: "#00c0ff",
    3500: "#00eaff",
    3000: "#00ffe4",
    2500: "#00ffd2",
    2000: "#00ff9c",
    1500: "#00ff72",
    1200: "#00ff36",
    1000: "#00ff0c",
    800: "#1eff00",
    600: "#42ff00",
    400: "#ccff00",
    300: "#f0ff00",
    200: "#ffea00",
    100: "#ffe062",
}