import unittest
from unittest import TestCase
from collision import *
from pygame.math import Vector2


class RectRectTests(TestCase):
    def assertColliding(self, center, size, expected):
        r1c = Vector2(center)
        r1s = size
        r2c = Vector2(30, 20)
        r2s = (10, 5)
        result = rect_rect(r1c, r1s, r2c, r2s)
        self.assertEqual(expected, result)

    def test_above_notColliding(self):
        self.assertColliding((30, 10), (1, 4), False)

    def test_touchingTop_notColliding(self):
        self.assertColliding((30, 10), (1, 5), False)

    def test_intrudingTop_colliding(self):
        self.assertColliding((30, 10), (1, 6), Vector2(0, -1))

    def test_below_notColliding(self):
        self.assertColliding((30, 30), (1, 4), False)

    def test_touchingBottom_notColliding(self):
        self.assertColliding((30, 30), (1, 5), False)

    def test_intrudingBottom_colliding(self):
        self.assertColliding((30, 30), (1, 6), Vector2(0, 1))

    def test_left_notColliding(self):
        self.assertColliding((10, 20), (9, 1), False)

    def test_touchingLeft_notColliding(self):
        self.assertColliding((10, 20), (10, 1), False)

    def test_intrudingLeft_colliding(self):
        self.assertColliding((10, 20), (11, 1), Vector2(-1, 0))

    def test_right_notColliding(self):
        self.assertColliding((50, 20), (9, 1), False)

    def test_touchingRight_notColliding(self):
        self.assertColliding((50, 20), (10, 1), False)

    def test_intrudingRight_colliding(self):
        self.assertColliding((50, 20), (11, 1), Vector2(1, 0))

    def test_sharedCenter_colliding(self):
        self.assertColliding((30, 20), (1, 1), Vector2(0, 6))


    def test_cornerIntrusionXUpperLeft_projectionSmallest(self):
        self.assertColliding((20, 15), (1, 2), Vector2(-1, 0))

    def test_cornerIntrusionXLowerLeft_projectionSmallest(self):
        self.assertColliding((20, 25), (1, 2), Vector2(-1, 0))

    def test_cornerIntrusionXUpperRight_projectionSmallest(self):
        self.assertColliding((40, 15), (1, 2), Vector2(1, 0))

    def test_cornerIntrusionXLowerRight_projectionSmallest(self):
        self.assertColliding((40, 25), (1, 2), Vector2(1, 0))


    def test_cornerIntrusionYUpperLeft_projectionSmallest(self):
        self.assertColliding((20, 15), (2, 1), Vector2(0, -1))

    def test_cornerIntrusionYLowerLeft_projectionSmallest(self):
        self.assertColliding((20, 25), (2, 1), Vector2(0, 1))

    def test_cornerIntrusionYUpperRight_projectionSmallest(self):
        self.assertColliding((40, 15), (2, 1), Vector2(0, -1))

    def test_cornerIntrusionYLowerRight_projectionSmallest(self):
        self.assertColliding((40, 25), (2, 1), Vector2(0, 1))

if __name__ == '__main__':
    unittest.main()
