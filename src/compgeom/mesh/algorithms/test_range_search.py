import unittest
import numpy as np
from range_search import RangeSearch

class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class TestRangeSearch(unittest.TestCase):
    def test_point3d_search(self):
        pts = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(5, 5, 5)]
        rs = RangeSearch(pts)
        
        # Test sphere
        indices = rs.within_sphere(Point3D(0.5, 0.5, 0.5), 1.0)
        self.assertIn(0, indices)
        self.assertIn(1, indices)
        self.assertEqual(len(indices), 2)
        
        # Test cube
        indices = rs.within_cube(Point3D(5, 5, 5), 0.1)
        self.assertEqual(indices, [2])

    def test_point2d_search(self):
        pts = [Point2D(0, 0), Point2D(1, 1), Point2D(5, 5)]
        rs = RangeSearch(pts)
        
        # Test square
        indices = rs.within_square(Point2D(0.5, 0.5), 0.6)
        self.assertIn(0, indices)
        self.assertIn(1, indices)
        self.assertEqual(len(indices), 2)

    def test_box_search(self):
        pts = [Point3D(i, i, i) for i in range(10)]
        rs = RangeSearch(pts)
        
        min_pt = Point3D(2.5, 2.5, 2.5)
        max_pt = Point3D(5.5, 5.5, 5.5)
        indices = rs.within_box(min_pt, max_pt)
        # Should contain indices 3, 4, 5
        self.assertEqual(sorted(indices), [3, 4, 5])

if __name__ == '__main__':
    unittest.main()
