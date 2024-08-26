# Plane Tracker

## Setting up

```sh
git clone https://github.com/KonradowyPL/planeTracker.git
cd planeTracker
pip install -r requirements.txt
touch config.json
```

In `config.json` add folowing:

```json
{
  "webhook": "WEBHOOK URL",
  "name": "Plane Spotter",
  "icon": "https://example.com/icon.png",
  "interval": 60,
  "color": "blue",
  "embedColor": "2CA3DA",
  "planes": ["HB-LUN", "HB-LUZ"],
  "bounds": "56.86,48.22,11.06,28.26"
}
```

where:

- `webhook` is your discord webhook url
- `name` is username of your discord bot
- `icon` is link to your discord bot avatar
- `interval` is interval where planes are checked in
- `color` is color of plane trace in hex or from [Pillow list of collors](https://pillow.readthedocs.org/en/latest/reference/ImageColor.html#color-names)
- `embedColor` is hex color of the sidebar of the embed. In this case light blue
- `planes` is array of plane resistration numbers, that you want to track
- `bounds` is an area where are planes you want to track in form of coma separated values:
  - max lat,
  - min lat,
  - max lon,
  - min lon
