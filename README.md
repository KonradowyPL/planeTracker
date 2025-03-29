<img src ="https://github.com/user-attachments/assets/6a19c889-326e-4bef-b1b7-9731352b6172" align="right" width="40%">

# Plane Tracker

A simple python code to track planes and notify you via discord webhooks
> [!WARNING]
> This should be used for your own educational purposes. If you are interested in accessing Flightradar24 data commercially, please contact business@fr24.com. See more information at [Flightradar24's terms and conditions](https://www.flightradar24.com/terms-and-conditions).

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
  "color": "blue",
  "embedColor": "2CA3DA",
  "planes": ["HB-LUN", "HB-LUZ"],
  "font": "/path/to/font.ttf"
}
```

where:

- `webhook` is your Discord webhook URL.
- `name` is the username of your Discord bot.
- `icon` is the link to your Discord bot avatar.
- `color` is the color of the plane trace in hex or from [Pillow's list of colors](https://pillow.readthedocs.io/en/latest/reference/ImageColor.html#color-names). If you remove this field, line color will be calculated according to [this](https://support.fr24.com/support/solutions/articles/3000115027-why-does-the-aircraft-s-trail-change-colour)
- `embedColor` is the hex color of the sidebar of the embed. In this case, light blue.
- `planes` is an array of plane registration numbers that you want to track.
- `font` is path to ttf font file. If not specifed defeault one will be used.
 

Note: Live mode, that periodically checks for new takeofs and landings has been discontinued. If you still want to acces it, it will be avaiable on `live-mode` branch.

## Contributing
Feel free to open issues and make PRs.

## License
This repository is under MIT license. See [license](./LICENSE) file.
