import os
import math
from PIL import Image
from io import BytesIO
from staticmap import Line

from src.map import AttribStaticMap, ramIcon
from src.orto_detection import hasOppositeSpikes
from src.utils import config, bounds, interpolate, distance, lineColor

arrival = Image.open(open("./src/arrival.png", "rb"))
departure = Image.open(open("./src/departure.png", "rb"))


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
    # if not orto:
    #     return None, feedback

    m = AttribStaticMap(2048, 1024, 8, 8)

    # draw path
    previous = coordinates[0]
    for point in coordinates[1:]:
        line = Line([previous, point], lineColor(point[2]), 2, simplify=False)
        m.add_line(line)
        previous = point

    # draw departure icon
    m.add_marker(
        ramIcon(
            coordinates[0], departure, departure.size[0] >> 1, departure.size[1] + 5
        )
    )

    # draw arrival icon
    m.add_marker(
        ramIcon(coordinates[-1], arrival, arrival.size[0] >> 1, arrival.size[1] + 5)
    )

    image = m.render()
    buffer = BytesIO()
    image.save(buffer, format="WEBP")
    buffer.seek(0)
    return buffer, feedback


def isOrto(coordinates) -> tuple[bool, dict]:
    resolution = 20  # ~5.5km
    spaced = resamplePolyline(coordinates, 1 / resolution)

    headings = [0.0] * 360
    prev = spaced[0]

    for point in spaced[1:]:
        delta = (point[0] - prev[0], point[1] - prev[1])

        angleRad = math.atan2(delta[0], delta[1])
        angleDeg = int(math.degrees(angleRad)) % 360

        for angle in range(angleDeg - 10, angleDeg + 10):
            headings[angle % 360] += 1

        prev = point

    result, data = hasOppositeSpikes(headings)
    return True, data


# resamples points so their distance is close to `spacing` degrees
def resamplePolyline(points, spacing):
    cumulativeLengths = [0.0]

    for i in range(1, len(points)):
        segLength = distance(points[i - 1], points[i])
        cumulativeLengths.append(cumulativeLengths[-1] + segLength)

    totalLength = cumulativeLengths[-1]

    if totalLength == 0:
        return [points[0]]

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
