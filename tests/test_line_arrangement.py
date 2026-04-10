import unittest
from compgeom.kernel import Point2D
from compgeom.cli.line_arrangement_cli import analyze_arrangement

class ArrangementTests(unittest.TestCase):
    def test_rectangle_arrangement_produces_one_face(self):
        segments = [
            (Point2D(0, 0), Point2D(1, 0)),
            (Point2D(1, 0), Point2D(1, 1)),
            (Point2D(1, 1), Point2D(0, 1)),
            (Point2D(0, 1), Point2D(0, 0)),
        ]
        intersections, split_segments, polygons = analyze_arrangement(segments)
        self.assertEqual(len(intersections), 4)
        self.assertEqual(len(split_segments), 4)
        self.assertEqual(len(polygons), 1)
        self.assertEqual(len(polygons[0]), 4)

if __name__ == "__main__":
    unittest.main()
