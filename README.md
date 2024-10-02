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
 
Now add mode: `live` or `summary` <br>
Summary means checking once a day for all flights. To activate it simply add this to Your JSON

```json
   "mode":"summary"
```

`live` mode is a mode, that checks more frequently (eg: once a minute) for launches and langings and notifes You about them. To activate it add folowing lines to Your JSON:

```json
  "mode": "live",
  "interval": 60,
  "checkHours": [9, 18],
  "checkDays": [0, 1, 2, 3, 4],
  "bounds": "56.86,48.22,11.06,28.26"
```

where:

- `interval` is the interval at which planes are checked.
- `checkHours` is an array where the first and second values define the range of hours during which your code will check for planes. In this example, checks will be performed between 9 AM and 6 PM. Useful when you don't want to check during the night.
- `checkDays` is an array of weekday integers where Monday == 0 and Sunday == 6. In this example, checks will be performed between Monday and Friday. Useful if the planes you want to track don't fly during weekends and you want to save on bandwidth.
- `bounds` is the area where the planes you want to track are located, in the form of comma-separated values:
  - max lat,
  - min lat,
  - max lon,
  - min lon


## Contributing
Feel free to open issues and make PRs.

## License
This repository is under MIT license. See [license](./LICENSE) file.
