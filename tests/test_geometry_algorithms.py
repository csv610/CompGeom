import math
import unittest
from pathlib import Path
import sys


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from geometry_utils import Point
from cli.line_arrangement import analyze_arrangement
from cli.polygon_boolean_operations import apply_boolean_operation
from trianglemesh.bounding import minimum_bounding_box, minimum_enclosing_circle
from trianglemesh.medial_axis import approximate_medial_axis
from trianglemesh.mesh import mesh_neighbors
from trianglemesh.path import shortest_path
from trianglemesh.triangulation import triangulate


class BoundingShapeTests(unittest.TestCase):
    def test_minimum_enclosing_circle_for_rectangle(self):
        points = [Point(0, 0), Point(2, 0), Point(2, 1), Point(0, 1)]
        center, radius = minimum_enclosing_circle(points)
        self.assertAlmostEqual(center.x, 1.0, places=6)
        self.assertAlmostEqual(center.y, 0.5, places=6)
        self.assertAlmostEqual(radius, math.sqrt(1.25), places=6)

    def test_minimum_bounding_box_for_rotated_diamond(self):
        points = [Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0)]
        box = minimum_bounding_box(points)
        self.assertAlmostEqual(box["area"], 2.0, places=6)
        self.assertAlmostEqual(box["width"], math.sqrt(2.0), places=6)
        self.assertAlmostEqual(box["height"], math.sqrt(2.0), places=6)


class PolygonBooleanTests(unittest.TestCase):
    def test_difference_with_nested_polygon_returns_region_with_hole(self):
        outer = [Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)]
        inner = [Point(1, 1), Point(3, 1), Point(3, 3), Point(1, 3)]
        result = apply_boolean_operation(outer, inner, "difference")
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["holes"]), 1)
        self.assertEqual(len(result[0]["outer"]), 4)
        self.assertEqual(len(result[0]["holes"][0]), 4)

    def test_union_of_overlapping_rectangles_returns_single_region(self):
        left = [Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]
        right = [Point(1, 1), Point(3, 1), Point(3, 3), Point(1, 3)]
        result = apply_boolean_operation(left, right, "union")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["holes"], [])


class MeshNeighborTests(unittest.TestCase):
    def test_mesh_neighbors_for_two_triangle_patch(self):
        triangles = [
            (Point(0, 0, 0), Point(1, 0, 1), Point(0, 1, 2)),
            (Point(1, 0, 1), Point(1, 1, 3), Point(0, 1, 2)),
        ]
        neighbors = mesh_neighbors(triangles)
        self.assertEqual(neighbors["vertex_neighbors"][1], [0, 2, 3])
        self.assertEqual(neighbors["triangle_neighbors"][0], [1])
        self.assertEqual(neighbors["triangle_neighbors"][1], [0])


class MeshPathTests(unittest.TestCase):
    def setUp(self):
        self.triangles = [
            (Point(0, 0, 0), Point(1, 0, 1), Point(0, 1, 2)),
            (Point(1, 0, 1), Point(1, 1, 3), Point(0, 1, 2)),
        ]

    def test_true_shortest_path_allows_direct_visibility(self):
        path, total_length = shortest_path(
            self.triangles,
            Point(0.1, 0.1),
            Point(0.9, 0.9),
            mode="true",
        )
        self.assertEqual(len(path), 2)
        self.assertAlmostEqual(total_length, math.sqrt((0.8**2) * 2), places=6)

    def test_edge_shortest_path_requires_points_on_mesh_edges_or_vertices(self):
        with self.assertRaisesRegex(ValueError, "Edge mode requires"):
            shortest_path(
                self.triangles,
                Point(0.1, 0.1),
                Point(0.9, 0.9),
                mode="edges",
            )

    def test_edge_shortest_path_between_vertices_uses_mesh_edges(self):
        path, total_length = shortest_path(
            self.triangles,
            Point(0, 0, 0),
            Point(1, 1, 3),
            mode="edges",
        )
        self.assertEqual(len(path), 3)
        self.assertAlmostEqual(total_length, 2.0, places=6)


class ArrangementTests(unittest.TestCase):
    def test_rectangle_arrangement_produces_one_face(self):
        segments = [
            (Point(0, 0), Point(1, 0)),
            (Point(1, 0), Point(1, 1)),
            (Point(1, 1), Point(0, 1)),
            (Point(0, 1), Point(0, 0)),
        ]
        intersections, split_segments, polygons = analyze_arrangement(segments)
        self.assertEqual(len(intersections), 4)
        self.assertEqual(len(split_segments), 4)
        self.assertEqual(len(polygons), 1)
        self.assertEqual(len(polygons[0]), 4)


class TriangulationTests(unittest.TestCase):
    def test_square_triangulates_into_two_faces(self):
        points = [Point(0, 0, 0), Point(1, 0, 1), Point(0, 1, 2), Point(1, 1, 3)]
        triangles, skipped = triangulate(points)
        self.assertEqual(len(skipped), 0)
        self.assertEqual(len(triangles), 2)
        vertex_ids = sorted(sorted(vertex.id for vertex in triangle) for triangle in triangles)
        self.assertEqual(vertex_ids, [[0, 1, 2], [1, 2, 3]])


class MedialAxisTests(unittest.TestCase):
    def test_square_medial_axis_produces_interior_graph(self):
        polygon = [Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]
        result = approximate_medial_axis(polygon, max_segment_length=0.5)
        self.assertGreater(len(result["samples"]), 4)
        self.assertGreater(len(result["centers"]), 0)
        self.assertGreater(len(result["segments"]), 0)
        for start, end in result["segments"]:
            self.assertTrue(0.0 <= start.x <= 2.0 and 0.0 <= start.y <= 2.0)
            self.assertTrue(0.0 <= end.x <= 2.0 and 0.0 <= end.y <= 2.0)


if __name__ == "__main__":
    unittest.main()
