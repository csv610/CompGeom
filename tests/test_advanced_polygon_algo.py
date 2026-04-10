import unittest
import math
from compgeom.kernel import Point2D
from compgeom.polygon import (
    compute_visibility_polygon,
    shortest_path_in_polygon,
    triangulate_polygon_with_holes
)

class AdvancedPolygonAlgorithmTests(unittest.TestCase):
    def test_compute_visibility_polygon_matches_convex_square(self):
        polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
        visible = compute_visibility_polygon(Point2D(2, 2), polygon)
        self.assertEqual(len(visible), 4)
        expected = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
        actual = [(round(point.x, 6), round(point.y, 6)) for point in visible]
        self.assertEqual(actual, expected)

    def test_shortest_path_in_concave_polygon_uses_reflex_vertex(self):
        polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
        path, total_length = shortest_path_in_polygon(polygon, Point2D(1, 3), Point2D(3, 3))
        self.assertEqual(path, [Point2D(1, 3), Point2D(2, 2), Point2D(3, 3)])
        self.assertAlmostEqual(total_length, 2.0 * math.sqrt(2.0), places=6)

    def test_triangulate_polygon_with_holes_preserves_area(self):
        outer = [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)]
        holes = [[Point2D(2, 2), Point2D(4, 2), Point2D(4, 4), Point2D(2, 4)]]
        triangles, merged = triangulate_polygon_with_holes(outer, holes)
        self.assertEqual(len(triangles), 8)
        self.assertEqual(len(merged), 10)
        covered_area = 0.0
        for a, b, c in triangles:
            covered_area += abs(
                (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0
            )
        self.assertAlmostEqual(covered_area, 32.0, places=6)

if __name__ == "__main__":
    unittest.main()
