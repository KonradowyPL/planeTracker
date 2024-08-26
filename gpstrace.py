from staticmap import StaticMap, Line, IconMarker
from io import BytesIO
from PIL import Image
import json

config = json.load(open("config.json", "r"))

icon = open("./icon.png", "rb")


class ramIcon(IconMarker):
    def __init__(self, coord, image, offset_x, offset_y):
        self.coord = coord
        self.img = image  # do not load img from disk
        self.offset = (offset_x, offset_y)

def makeTrace(points):
    try:
        return _makeTrace(points)
    except Exception as error:
        print("\n", error,"\n")
        return None

def _makeTrace(points):
    coordinates = [(point["lng"], point["lat"]) for point in points]
    m = StaticMap(1024, 512, 8, 8)

    line = Line(coordinates, config.get("color", "green"), 2, simplify=False)
    m.add_line(line)
    newImg = Image.open(icon)
    newImg = newImg.rotate(90 - points[0]["hd"], expand=True, resample=Image.BICUBIC)
    marker = ramIcon(coordinates[0], newImg, newImg.size[0] >> 1, newImg.size[1] >> 1)
    m.add_marker(marker)

    image = m.render()
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer
