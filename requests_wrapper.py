import requests
import json
from utils import config
url = config['flareSolver']
headers = {"Content-Type": "application/json"}


def get(targetUrl: str) -> str:
    payload = {"cmd": "request.get", "url": targetUrl, "maxTimeout": 60000}
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    return data["solution"]["response"]


def toJson(data:str):
  data = data.removeprefix('<html><head><meta name="color-scheme" content="light dark"><meta charset="utf-8"></head><body><pre>')
  data = data.removesuffix('</pre><div class="json-formatter-container"></div></body></html>')
  return json.loads(data)