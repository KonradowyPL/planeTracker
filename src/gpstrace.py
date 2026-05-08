from staticmap import StaticMap, Line, IconMarker
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from collections import defaultdict
from src.utils import config, colors, bounds
import math
from src.orto_detection import hasOppositeSpikes

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

    def _draw_base_layer(self, image):
        return


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


def makeTrace(points) -> tuple[BytesIO | None, dict]:
    if len(points) < 1:
        return None, {"msg": "no trace"}

    coordinates = [
        (point["longitude"], point["latitude"], point["altitude"]["meters"])
        for point in points
    ]

    if bounds and not inBounds(coordinates):
        return None, {"msg": "out of bounds"}

    # config.get("orto") and
    orto, feedback = isOrto(coordinates)
    if not orto:
        return None, feedback

    m = AttribStaticMap(1024, 512, 8, 8)

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
    newImg = newImg.rotate(
        90 - points[0]["heading"], expand=True, resample=Image.Resampling.BICUBIC
    )
    marker = ramIcon(coordinates[0], newImg, newImg.size[0] >> 1, newImg.size[1] >> 1)
    m.add_marker(marker)

    image = m.render()
    buffer = BytesIO()
    image.save(buffer, format="WEBP")
    buffer.seek(0)
    return buffer, feedback


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


def isOrto(coordinates):
    resolution = 20
    spaced = resamplePolyline(coordinates, 1 / resolution)

    headings = [0.0] * 360

    prev = spaced[0]

    for point in spaced[1:]:
        delta = (point[0] - prev[0], point[1] - prev[1])

        angleRad = math.atan2(delta[1], delta[0])
        angleDeg = int(math.degrees(angleRad)) % 360

        for angle in range(angleDeg - 10, angleDeg + 10):
            headings[angle % 360] += 1

        prev = point

    # print(headings)
    result, data = hasOppositeSpikes(headings)
    return True, data


def distance(pointA, pointB):
    dx = pointB[0] - pointA[0]
    dy = pointB[1] - pointA[1]
    return math.hypot(dx, dy)


def interpolate(pointA, pointB, t):
    return (
        pointA[0] + (pointB[0] - pointA[0]) * t,
        pointA[1] + (pointB[1] - pointA[1]) * t,
        pointA[2] + (pointB[2] - pointA[2]) * t,
    )


def resamplePolyline(points, spacing):
    """
    Resample a polyline so points are evenly spaced.

    Args:
        points: list of (x, y) tuples
        spacing: desired distance between output points

    Returns:
        list of evenly spaced (x, y) tuples
    """

    if len(points) < 2:
        return points[:]

    # Compute cumulative arc lengths
    cumulativeLengths = [0.0]

    for i in range(1, len(points)):
        segLength = distance(points[i - 1], points[i])
        cumulativeLengths.append(cumulativeLengths[-1] + segLength)

    totalLength = cumulativeLengths[-1]

    if totalLength == 0:
        return [points[0]]

    # Generate target distances
    numSamples = max(1, int(round(totalLength / spacing)))
    targetDistances = [i * totalLength / numSamples for i in range(numSamples + 1)]

    result = []

    segIndex = 0

    for targetDist in targetDistances:
        while (
            segIndex < len(cumulativeLengths) - 2
            and cumulativeLengths[segIndex + 1] < targetDist
        ):
            segIndex += 1

        segStartDist = cumulativeLengths[segIndex]
        segEndDist = cumulativeLengths[segIndex + 1]

        if segEndDist == segStartDist:
            result.append(points[segIndex])
            continue

        t = (targetDist - segStartDist) / (segEndDist - segStartDist)

        newPoint = interpolate(
            points[segIndex],
            points[segIndex + 1],
            t,
        )

        result.append(newPoint)

    return result
