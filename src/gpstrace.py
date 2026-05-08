from staticmap import StaticMap, Line, IconMarker
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from collections import defaultdict
from src.utils import config, colors, bounds

icon = open("./src/icon.png", "rb")


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

    def determine_extent(self, zoom=None) -> tuple[float, float, float, float]:
        if self.extent is None:
            return super().determine_extent(zoom)
        return max(self.extent, super().determine_extent(zoom))


def inBounds(coordinates: list[tuple[float, float, float]]):
    for pos in coordinates:
        if (
            pos[1] < bounds[0]
            and pos[1] > bounds[1]
            and pos[0] > bounds[2]
            and pos[0] < bounds[3]
        ):
            return True
    return False


def makeTrace(points):
    if len(points) < 1:
        return None

    coordinates = [
        (point["lng"], point["lat"], point["alt"] * 0.3048) for point in points
    ]

    if bounds and not inBounds(coordinates):
        return None

    m = AttribStaticMap(1024, 512, 8, 8)

    if config.get("clipOrtophoto"):
        minlng, maxlng, minlat, maxlat = get_bounding_box(coordinates)
        if minlat < 100 and minlng < 100:
            m.extent = (minlng, minlat, maxlng, maxlat)
            m.padding = 100, 100

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


def convert(points, distance_apart: int | float = 1):
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
    resolution = 30

    spaced = convert(coordinates, distance_apart=1 / resolution)
    squares = find_dense_squares(spaced, resolution=resolution)

    minlng = minlat = 360
    maxlng = maxlat = -360

    for square in squares:
        this = squares[square]
        if this >= 3:
            # m.add_marker(IconMarker(square, "./icon.png", 22, 22))
            minlng = min(minlng, square[0])
            maxlng = max(maxlng, square[0])
            minlat = min(minlat, square[1])
            maxlat = max(maxlat, square[1])

    minlng += 1 / resolution
    maxlng += 1 / resolution
    minlat += 1 / resolution
    maxlat += 1 / resolution

    return minlng, maxlng, minlat, maxlat
