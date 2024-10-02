from staticmap import StaticMap, Line, IconMarker, Polygon
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import json
import numpy as np
from collections import defaultdict

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


def makeTrace(points):
    return _makeTrace(points)


def _makeTrace(points):
    coordinates = [(point["lng"], point["lat"], point['alt'] * 0.3048) for point in points]
    m = AttribStaticMap(1024, 512, 8, 8)

    if config.get("debug_bbox_render"):
        minlat, maxlat, minlng, maxlng = get_bounding_box(coordinates)
        if minlat < 100 and minlng < 100:
            m.add_line(
                Line(
                    [
                        [minlat, minlng],
                        [minlat, maxlng],
                        [maxlat, maxlng],
                        [maxlat, minlng],
                        [minlat, minlng],
                    ],
                    "#ff000040",
                    2,
                )
            )
    if color := config.get("color"):
        line = Line(coordinates, color, 2, simplify=False)
        m.add_line(line)
    else:
        current = ()
        for index, point in enumerate(coordinates):
            if index == 0:
                current = point
                continue
            line = Line([current, point], lineColor(point[2]), 2, simplify=False)
            m.add_line(line)
            current = point

    newImg = Image.open(icon)
    newImg = newImg.rotate(90 - points[0]["hd"], expand=True, resample=Image.BICUBIC)
    marker = ramIcon(coordinates[0], newImg, newImg.size[0] >> 1, newImg.size[1] >> 1)
    m.add_marker(marker)

    image = m.render()
    buffer = BytesIO()
    image.save(buffer, format="WEBP")
    buffer.seek(0)
    return buffer


def convert(points, distance_apart=1):
    current = (99999, 99999)
    new = []
    for point in points:
        newx, newy = (
            int(point[0] / distance_apart) * distance_apart,
            int(point[1] / distance_apart) * distance_apart,
        )
        if current != (newx, newy):
            new.append((newx, newy))
            current = (newx, newy)

    return new


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


def lineColor(height):
    closest_key = min(colors.keys(), key=lambda k: abs(k - height))
    return colors[closest_key]


def find_dense_squares(points, resolution):
    # Dictionary to count points in each 1x1 square
    square_count = defaultdict(int)

    # Count points in each square
    for x, y in points:
        # Find the bottom-left corner of the square for each point
        square = (int(x * resolution) / resolution, int(y * resolution) / resolution)
        square_count[square] += 1
    return square_count


def get_bounding_box(coordinates):
    resolution = 1 / 0.1

    spaced = convert(coordinates, distance_apart=1 / resolution)
    squares = find_dense_squares(spaced, resolution=resolution)

    minlat = minlng = 360
    maxlat = maxlng = -360

    for square in squares:
        this = squares[square]
        if this >= 2:
            # m.add_marker(IconMarker(square, "./icon.png", 22, 22))
            minlat = min(minlat, square[0])
            maxlat = max(maxlat, square[0])
            minlng = min(minlng, square[1])
            maxlng = max(maxlng, square[1])

    minlat += 0.5 / resolution
    maxlat += 0.5 / resolution
    minlng += 0.5 / resolution
    maxlng += 0.5 / resolution

    return minlat, maxlat, minlng, maxlng
