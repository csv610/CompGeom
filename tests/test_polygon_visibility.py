import unittest
from compgeom.kernel import Point2D
from compgeom.cli.polygon_visibility_cli import parse_input as parse_visibility_input, visible_boundary_segments

class PolygonVisibilityTests(unittest.TestCase):
    def test_visibility_parser_accepts_query_and_polygon(self):
        query, polygon = parse_visibility_input(
            [
                "1 2\n",
                "0 0\n",
                "4 0\n",
                "4 3\n",
                "0 3\n",
            ]
        )
        self.assertEqual(query, Point2D(1, 2))
        self.assertEqual(len(polygon), 4)

    def test_visible_segments_are_subdivided_for_concave_polygon(self):
        polygon = [
            Point2D(0, 0),
            Point2D(5, 0),
            Point2D(5, 1),
            Point2D(2, 1),
            Point2D(2, 4),
            Point2D(5, 4),
            Point2D(5, 5),
            Point2D(0, 5),
        ]
        segments = visible_boundary_segments(Point2D(1, 2.5), polygon)
        self.assertEqual(len(segments), 4)
        self.assertAlmostEqual(segments[0][0].x, 0.0, places=6)
        self.assertAlmostEqual(segments[0][0].y, 0.0, places=6)
        self.assertAlmostEqual(segments[0][1].x, 8.0 / 3.0, places=6)
        self.assertAlmostEqual(segments[0][1].y, 0.0, places=6)
        self.assertEqual(segments[1], (Point2D(2, 1), Point2D(2, 4)))
        self.assertAlmostEqual(segments[2][0].x, 8.0 / 3.0, places=6)
        self.assertAlmostEqual(segments[2][0].y, 5.0, places=6)
        self.assertAlmostEqual(segments[2][1].x, 0.0, places=6)
        self.assertAlmostEqual(segments[2][1].y, 5.0, places=6)
        self.assertEqual(segments[3], (Point2D(0, 5), Point2D(0, 0)))

    def test_outside_query_sees_only_exposed_boundary(self):
        polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
        segments = visible_boundary_segments(Point2D(5, 2), polygon)
        self.assertEqual(segments, [(Point2D(4, 0), Point2D(4, 4))])

if __name__ == "__main__":
    unittest.main()
