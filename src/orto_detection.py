from typing import List, Tuple


def angularDistance(a: int, b: int) -> int:
    """
    Circular angular distance on a 360° ring.
    """
    diff = abs(a - b)
    return min(diff, 360 - diff)


def findPeaks(data: List[float], thresholdRatio: float = 0.6) -> List[int]:
    """
    Find strong local maxima.
    """

    maxValue = max(data)
    threshold = maxValue * thresholdRatio

    peaks = []

    for i in range(360):
        prevValue = data[(i - 1) % 360]
        currValue = data[i]
        nextValue = data[(i + 1) % 360]

        if (
            currValue >= threshold
            and currValue >= prevValue
            and currValue >= nextValue
        ):
            peaks.append(i)

    return peaks


def hasOppositeSpikes(
    data: List[float],
    angleTolerance: int = 15,
    heightTolerance: float = 0.30,
) -> Tuple[bool, dict]:
    """
    Detect two roughly equal spikes about 180° apart.

    Parameters
    ----------
    angleTolerance:
        allowed deviation from 180°

    heightTolerance:
        allowed relative height mismatch
        0.30 => peaks may differ by 30%
    """

    if len(data) != 360:
        raise ValueError("Dataset must contain exactly 360 elements")

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