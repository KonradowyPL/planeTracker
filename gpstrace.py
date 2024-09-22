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
        _,_,text_width, text_height = draw.textbbox((0,0), self.attribution, font=font)
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
    # try:
    return _makeTrace(points)


# except Exception as error:
# print("\n", error, "\n")
# return None


def _makeTrace(points):
    coordinates = [(point["lng"], point["lat"]) for point in points]
    m = AttribStaticMap(1024, 512, 8, 8)

    if config.get("debug_bbox_render"):
        minlat, maxlat, minlng, maxlng = get_bounding_box(coordinates)    

        m.add_line(
            Line(
                [
                    [minlat, minlng],
                    [minlat, maxlng],
                    [maxlat, maxlng],
                    [maxlat, minlng],
                    [minlat, minlng],
                ],
                "red",
                2,
            )
        )

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


def distance(p1, p2):
    """Calculate the Euclidean distance between two points."""
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def interpolate_points(p1, p2, t):
    """Linearly interpolate between points p1 and p2 by a factor t."""
    return [(1 - t) * p1[0] + t * p2[0], (1 - t) * p1[1] + t * p2[1]]


def convert(points, distance_apart=1):
    """Resample the line such that points are approximately `distance_apart` units apart."""

    # Calculate cumulative distances along the line
    cum_distances = [0]
    for i in range(1, len(points)):
        cum_distances.append(cum_distances[-1] + distance(points[i - 1], points[i]))

    # Total length of the line
    total_length = cum_distances[-1]

    # Generate new equally spaced distances
    new_distances = np.arange(0, total_length, distance_apart)

    # Resample points
    new_points = [points[0]]  # Start with the first point
    current_point_index = 0

    for d in new_distances[1:]:  # Skip the first point
        # Find where the new distance falls between two original points
        while cum_distances[current_point_index + 1] < d:
            current_point_index += 1

        # Linearly interpolate between the two bounding points
        p1 = points[current_point_index]
        p2 = points[current_point_index + 1]
        t = (d - cum_distances[current_point_index]) / (
            cum_distances[current_point_index + 1] - cum_distances[current_point_index]
        )

        new_points.append(interpolate_points(p1, p2, t))

    return new_points


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

    spaced = convert(coordinates, distance_apart=0.01)
    squares = find_dense_squares(spaced, resolution=resolution)

    array = np.array(list(squares.values()))
    precentile = np.percentile(array, 60)

    minlat = minlng = 9999999999999999
    maxlat = maxlng = 0

    for square in squares:
        this = squares[square]
        if this >= precentile:
            # m.add_marker(IconMarker(square, "./icon.png", 22, 22))
            minlat = min(minlat, square[0])
            maxlat = max(maxlat, square[0])
            minlng = min(minlng, square[1])
            maxlng = max(maxlng, square[1])

    minlat += 0.5/resolution
    maxlat += 0.5/resolution
    minlng += 0.5/resolution
    maxlng += 0.5/resolution

    return minlat, maxlat, minlng, maxlng