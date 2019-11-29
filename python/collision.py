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
    :rtype: bool
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


def ellipticNormal(pos, obsPos, exponent):
    """
    Get the normal collision angle for a moving object with respect to an obstacle according to an elliptical model for the
    other object.
    :param pos: Moving object's center point
    :type pos: Vector2
    :param obsPos: Obstacle's center point
    :type obsPos: Vector2
    :param exponent: Exponent for the elliptical curve model (larger values being more rectangular)
    :type exponent: float
    :rtype: Vector2
    """
    diff = pos-obsPos
    absDiff = Vector2(abs(diff.x), abs(diff.y))

    angle = Vector2().angle_to(absDiff)
    ellipAngle = (angle/90)**exponent * 90

    if diff.x < 0:
        ellipAngle = 180 - ellipAngle
    if diff.y < 0:
        ellipAngle *= -1
    return vectorFromPolar((1, ellipAngle))


def vectorFromPolar(polar):
    """
    Get a vector from a polar coordinates tuple.
    :param polar: Tuple (r, phi) where r is the radial distance, and phi is the azimuthal angle
    :type polar: (float, float)
    :rtype: Vector2
    """
    v = Vector2()
    v.from_polar(polar)
    return v
