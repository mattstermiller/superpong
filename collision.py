from pygame.math import Vector2
import math


def rect_rect(r1c, r1s, r2c, r2s):
    """
    Get the projection vector of a rectangle colliding with another rectangle if they are colliding, False otherwise.
    :param r1c: First rectangle's center point
    :type r1c: Vector2
    :param r1s: First rectangle's half-size
    :type r1s: (float, float)
    :param r2c: Second rectangle's center point
    :type r2c: Vector2
    :param r2s: Second rectangle's half-size
    :type r2s: (float, float)
    :return: Projection vector for the first shape if the shapes are colliding, False otherwise
    """
    projection = []
    for diff, size in ((d1 - d2, s1 + s2) for d1, d2, s1, s2 in zip(r1c, r2c, r1s, r2s)):
        intrusion = size - abs(diff)
        if intrusion <= 0:
            return False
        else:
            projection.append(math.copysign(intrusion, diff))

    if abs(projection[0]) > abs(projection[1]):
        projection[0] = 0
    else:
        projection[1] = 0
    return Vector2(projection)
