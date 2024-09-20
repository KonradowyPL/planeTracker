from staticmap import StaticMap, Line, IconMarker
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import json

config = json.load(open("config.json", "r"))

icon = open("./icon.png", "rb")


class ramIcon(IconMarker):
    def __init__(self, coord, image, offset_x, offset_y):
        self.coord = coord
        self.img = image  # do not load img from disk
        self.offset = (offset_x, offset_y)


class AttribStaticMap(StaticMap, object):
    def __init__(self, *args, **kwargs):
        self.attribution = "© OpenStreetMap-Contributors"
        super(AttribStaticMap, self).__init__(*args, **kwargs)

    def _draw_features(self, image):
        super(AttribStaticMap, self)._draw_features(image)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(config.get("font"))
        except Exception:    
            font = ImageFont.load_default()
        image_width, image_height = image.size
        text_width, text_height = draw.textsize(self.attribution, font=font)
        padding = 2
        x = image_width - text_width - padding
        y = image_height - text_height - padding
        rectangle_x0 = x - padding
        rectangle_y0 = y - padding
        draw.rectangle(
            [(rectangle_x0, rectangle_y0), (image_width, image_height)], fill="white"
        )
        draw.text((x, y), self.attribution, font=font, fill="black")


def makeTrace(points):
    try:
        return _makeTrace(points)
    except Exception as error:
        print("\n", error, "\n")
        return None


def _makeTrace(points):
    coordinates = [(point["lng"], point["lat"]) for point in points]
    m = AttribStaticMap(1024, 512, 8, 8)

    line = Line(coordinates, config.get("color", "green"), 2, simplify=False)
    m.add_line(line)
    newImg = Image.open(icon)
    newImg = newImg.rotate(90 - points[0]["hd"], expand=True, resample=Image.BICUBIC)
    marker = ramIcon(coordinates[0], newImg, newImg.size[0] >> 1, newImg.size[1] >> 1)
    m.add_marker(marker)

    image = m.render()
    buffer = BytesIO()
    image.save(buffer, format="WEBP")
    buffer.seek(0)
    return buffer