# Plane Tracker

## Setting up

```sh
git clone https://github.com/KonradowyPL/planeTracker.git
cd planeTracker
pip install -r requirements.txt
touch config.json
```

In `config.json` add following:

```json
{
  "webhook": "WEBHOOK URL",
  "name": "Plane Spotter",
  "icon": "https://example.com/icon.png",
  "interval": 60,
  "color": "blue",
  "embedColor": "2CA3DA",
  "planes": ["HB-LUN", "HB-LUZ"],
  "checkHours": [9, 18],
  "checkDays": [0, 1, 2, 3, 4],
  "bounds": "56.86,48.22,11.06,28.26"
}
```

where:

- `webhook` is your Discord webhook URL.
- `name` is the username of your Discord bot.
- `icon` is the link to your Discord bot avatar.
- `interval` is the interval at which planes are checked.
- `color` is the color of the plane trace in hex or from [Pillow's list of colors](https://pillow.readthedocs.io/en/latest/reference/ImageColor.html#color-names).
- `embedColor` is the hex color of the sidebar of the embed. In this case, light blue.
- `planes` is an array of plane registration numbers that you want to track.
- `checkHours` is an array where the first and second values define the range of hours during which your code will check for planes. In this example, checks will be performed between 9 AM and 6 PM. Useful when you don't want to check during the night.
- `checkDays` is an array of weekday integers where Monday == 0 and Sunday == 6. In this example, checks will be performed between Monday and Friday. Useful if the planes you want to track don't fly during weekends and you want to save on bandwidth.
- `bounds` is the area where the planes you want to track are located, in the form of comma-separated values:
  - max lat,
  - min lat,
  - max lon,
  - min lon