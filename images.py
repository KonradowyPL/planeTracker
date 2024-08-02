import requests
from bs4 import BeautifulSoup
import json

try:
    data = dict(json.load(open("./imgCache.json", "r")))
except:  # noqa: E722
    data = {}

# gets image from plane registration number
# returns image url
def getImage(reg) -> str:
    # check if in img cache
    if reg in data:
        return data[reg]

    try:
        res = requests.get(
            f"https://www.jetphotos.com/photo/keyword/{reg}",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Sec-GPC": "1",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Priority": "u=0, i",
            },
        )
        if res.status_code != 200:
            print("Error finding image!")
            return ""

        html_soup = BeautifulSoup(res.text, "html.parser")
        image = html_soup.find('img', class_='result__photo')
        url = "https:" + image.get('src')
        data[reg] = url
        json.dump(data, open("./imgCache.json", "w"))
        return url
    except Exception as error: 
        print("Error finding image!", error)
        return ""
        


print(getImage("SP-FPK"))
