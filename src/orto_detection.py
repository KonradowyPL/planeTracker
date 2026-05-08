from src.utils import angularDistance


def findPeaks(data: list[float], thresholdRatio: float = 0.6) -> list[int]:
    maxValue = max(data)
    threshold = maxValue * thresholdRatio

    peaks = []

    for i in range(360):
        prevValue = data[(i - 1) % 360]
        currValue = data[i]
        nextValue = data[(i + 1) % 360]

        if currValue >= threshold and currValue >= prevValue and currValue >= nextValue:
            peaks.append(i)

    return peaks


def hasOppositeSpikes(
    data: list[float],
    angleTolerance: int = 15,
    heightTolerance: float = 0.30,
) -> tuple[bool, dict]:

    peaks = findPeaks(data)

    if len(peaks) < 2:
        return False, {"reason": "not enough peaks"}

    bestMatch = None

    for i in range(len(peaks)):
        for j in range(i + 1, len(peaks)):

            p1 = peaks[i]
            p2 = peaks[j]

            dist = angularDistance(p1, p2)

            angleError = abs(dist - 180)

            if angleError > angleTolerance:
                continue

            h1 = data[p1]
            h2 = data[p2]

            heightRatio = min(h1, h2) / max(h1, h2)

            if heightRatio < (1.0 - heightTolerance):
                continue

            score = angleError + (1.0 - heightRatio) * 100

            if bestMatch is None or score < bestMatch["score"]:
                bestMatch = {
                    "peak1Deg": p1,
                    "peak2Deg": p2,
                    "distanceDeg": dist,
                    "height1": h1,
                    "height2": h2,
                    "heightRatio": round(heightRatio, 3),
                    "score": round(score, 3),
                }

    if bestMatch is None:
        return False, {"reason": "no matching opposite peaks"}

    return True, bestMatch
