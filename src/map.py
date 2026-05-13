import os
import requests
from PIL import ImageFont, ImageDraw
from staticmap import StaticMap, IconMarker

from src.utils import config, bounds
from src.requests_wrapper import shouldDump, urlToFilename


class ramIcon(IconMarker):
    def __init__(self, coord, image, offset_x, offset_y):
        self.coord = coord
        self.img = image  # do not load img from disk
        self.offset = (offset_x, offset_y)


class AttribStaticMap(StaticMap, object):
    def __init__(self, *args, **kwargs):
        self.attribution = "© OpenStreetMap-Contributors"
        self.extent: tuple[float, float, float, float] | None = None
        super(AttribStaticMap, self).__init__(*args, **kwargs)
        self.headers = {"User-Agent": f"StaticMap-{config['userAgent']}"}
        self.url_template = "https://osm.rrze.fau.de/osmhd/{z}/{x}/{y}.png"
        self.tile_size = 512

    def _draw_features(self, image):
        super(AttribStaticMap, self)._draw_features(image)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(config.get("font"), 20)
        except Exception:
            font = ImageFont.load_default()
        image_width, image_height = image.size
        _, _, text_width, text_height = draw.textbbox(
            (0, 0), self.attribution, font=font
        )

        padding = 2
        x = image_width - text_width - padding
        y = image_height - text_height - padding
        rectangle_x0 = x - padding
        rectangle_y0 = y - padding
        draw.rectangle(
            [(rectangle_x0, rectangle_y0), (image_width, image_height)], fill="white"
        )
        draw.text((x, y), self.attribution, font=font, fill="black")

    def determine_extent(self, zoom=None) -> tuple[float, float, float, float]:
        if self.extent is None:
            return super().determine_extent(zoom)
        return max(self.extent, super().determine_extent(zoom))

    def get(self, url, **kwargs):
        fileName = "./dump/" + urlToFilename(url)
        dump = shouldDump(url)
        if dump and os.path.exists(fileName):
            return 200, open(fileName, "rb").read()

        res = requests.get(url, **kwargs)

        if dump:
            open(fileName, "wb").write(res.content)
        return res.status_code, res.content

