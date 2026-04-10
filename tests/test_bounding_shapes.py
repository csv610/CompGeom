import unittest
import math
from compgeom.kernel import Point2D
from compgeom.algo.bounding import minimum_bounding_box, minimum_enclosing_circle

class BoundingShapeTests(unittest.TestCase):
    def test_minimum_enclosing_circle_for_rectangle(self):
        points = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(0, 1)]
        center, radius = minimum_enclosing_circle(points)
        self.assertAlmostEqual(center.x, 1.0, places=6)
        self.assertAlmostEqual(center.y, 0.5, places=6)
        self.assertAlmostEqual(radius, math.sqrt(1.25), places=6)

    def test_minimum_bounding_box_for_rotated_diamond(self):
        points = [Point2D(0, 1), Point2D(1, 0), Point2D(0, -1), Point2D(-1, 0)]
        box = minimum_bounding_box(points)
        self.assertAlmostEqual(box["area"], 2.0, places=6)
        self.assertAlmostEqual(box["width"], math.sqrt(2.0), places=6)
        self.assertAlmostEqual(box["height"], math.sqrt(2.0), places=6)

if __name__ == "__main__":
    unittest.main()
