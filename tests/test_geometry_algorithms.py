import math
import unittest
from pathlib import Path
import sys


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from compgeom import Point2D
from compgeom.cli.line_arrangement_cli import analyze_arrangement
from compgeom.cli.polygon_visibility_cli import parse_input as parse_visibility_input, visible_boundary_segments
from compgeom.cli.reflection_polygon_cli import parse_input, simulate_reflections
from compgeom.cli.polygon_boolean_operations_cli import apply_boolean_operation
from compgeom import minimum_bounding_box, minimum_enclosing_circle
from compgeom import incircle_sign, orientation_sign
from compgeom import approximate_medial_axis
from compgeom import mesh_neighbors
from compgeom import shortest_path
from compgeom import DCEL
def locate_face(dcel, point): return dcel.locate_face(point)
from compgeom import shortest_path_in_polygon, triangulate_polygon_with_holes, compute_visibility_polygon
from compgeom import constrained_delaunay_triangulation, triangulate


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


class PredicateRobustnessTests(unittest.TestCase):
    def test_orientation_sign_handles_nearly_collinear_points(self):
        a = Point2D(0.0, 0.0)
        b = Point2D(1e-12, 1e-12)
        c = Point2D(2e-12, 3e-12)
        self.assertEqual(orientation_sign(a, b, c), 1)

    def test_incircle_sign_is_orientation_aware(self):
        a = Point2D(0, 0)
        b = Point2D(1, 0)
        c = Point2D(0, 1)
        inside = Point2D(0.2, 0.2)
        outside = Point2D(2, 2)
        self.assertEqual(incircle_sign(a, b, c, inside), 1)
        self.assertEqual(incircle_sign(c, b, a, inside), 1)
        self.assertEqual(incircle_sign(a, b, c, outside), -1)


class PolygonBooleanTests(unittest.TestCase):
    def test_difference_with_nested_polygon_returns_region_with_hole(self):
        outer = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
        inner = [Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)]
        result = apply_boolean_operation(outer, inner, "difference")
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["holes"]), 1)
        self.assertEqual(len(result[0]["outer"]), 4)
        self.assertEqual(len(result[0]["holes"][0]), 4)

    def test_union_of_overlapping_rectangles_returns_single_region(self):
        left = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
        right = [Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)]
        result = apply_boolean_operation(left, right, "union")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["holes"], [])


class MeshNeighborTests(unittest.TestCase):
    def test_mesh_neighbors_for_two_triangle_patch(self):
        triangles = [
            (Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2)),
            (Point2D(1, 0, 1), Point2D(1, 1, 3), Point2D(0, 1, 2)),
        ]
        neighbors = mesh_neighbors(triangles)
        self.assertEqual(neighbors["vertex_neighbors"][1], [0, 2, 3])
        self.assertEqual(neighbors["triangle_neighbors"][0], [1])
        self.assertEqual(neighbors["triangle_neighbors"][1], [0])


class MeshPathTests(unittest.TestCase):
    def setUp(self):
        self.triangles = [
            (Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2)),
            (Point2D(1, 0, 1), Point2D(1, 1, 3), Point2D(0, 1, 2)),
        ]

    def test_true_shortest_path_allows_direct_visibility(self):
        path, total_length = shortest_path(
            self.triangles,
            Point2D(0.1, 0.1),
            Point2D(0.9, 0.9),
            mode="true",
        )
        self.assertEqual(len(path), 2)
        self.assertAlmostEqual(total_length, math.sqrt((0.8**2) * 2), places=6)

    def test_edge_shortest_path_requires_points_on_mesh_edges_or_vertices(self):
        with self.assertRaisesRegex(ValueError, "Edge mode requires"):
            shortest_path(
                self.triangles,
                Point2D(0.1, 0.1),
                Point2D(0.9, 0.9),
                mode="edges",
            )

    def test_edge_shortest_path_between_vertices_uses_mesh_edges(self):
        path, total_length = shortest_path(
            self.triangles,
            Point2D(0, 0, 0),
            Point2D(1, 1, 3),
            mode="edges",
        )
        self.assertEqual(len(path), 3)
        self.assertAlmostEqual(total_length, 2.0, places=6)


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


class ReflectionPolygonTests(unittest.TestCase):
    def test_parse_input_normalizes_direction_and_preserves_polygon(self):
        origin, direction, polygon = parse_input(
            [
                "1 1\n",
                "3 4\n",
                "0 0\n",
                "5 0\n",
                "5 5\n",
                "0 5\n",
            ]
        )
        self.assertEqual(origin, Point2D(1, 1))
        self.assertAlmostEqual(direction.x, 0.6, places=6)
        self.assertAlmostEqual(direction.y, 0.8, places=6)
        self.assertEqual(len(polygon), 4)

    def test_reflection_path_bounces_between_parallel_walls(self):
        polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2)]
        path = simulate_reflections(
            origin=Point2D(1, 1),
            direction=Point2D(1, 0.25),
            polygon=polygon,
            steps=4,
        )
        self.assertEqual(len(path), 5)
        self.assertAlmostEqual(path[1].x, 4.0, places=6)
        self.assertAlmostEqual(path[1].y, 1.75, places=6)
        self.assertAlmostEqual(path[2].x, 3.0, places=6)
        self.assertAlmostEqual(path[2].y, 2.0, places=6)
        self.assertAlmostEqual(path[3].x, 0.0, places=6)
        self.assertAlmostEqual(path[3].y, 1.25, places=6)
        self.assertAlmostEqual(path[4].x, 4.0, places=6)
        self.assertAlmostEqual(path[4].y, 0.25, places=6)

    def test_parse_input_rejects_origin_outside_polygon(self):
        with self.assertRaisesRegex(ValueError, "inside or on the boundary"):
            parse_input(
                [
                    "10 10\n",
                    "1 0\n",
                    "0 0\n",
                    "4 0\n",
                    "4 4\n",
                    "0 4\n",
                ]
            )


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


class PlanarSubdivisionTests(unittest.TestCase):
    def test_locate_face_for_polygon_with_hole(self):
        dcel = DCEL.from_polygon(
            [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)],
            holes=[[Point2D(2, 2), Point2D(4, 2), Point2D(4, 4), Point2D(2, 4)]],
        )
        interior = dcel.locate_face(Point2D(1, 1))
        hole_region = dcel.locate_face(Point2D(3, 3))
        exterior = dcel.locate_face(Point2D(7, 3))
        self.assertFalse(interior.is_exterior)
        self.assertTrue(hole_region.is_exterior)
        self.assertTrue(exterior.is_exterior)

    def test_polygon_dcel_has_expected_primitives(self):
        dcel = DCEL.from_polygon([Point2D(0, 0), Point2D(3, 0), Point2D(0, 2)])
        self.assertEqual(len(dcel.vertices), 3)
        self.assertEqual(len(dcel.half_edges), 6)
        self.assertEqual(len(dcel.faces), 2)


class TriangulationTests(unittest.TestCase):
    def test_square_triangulates_into_two_faces(self):
        points = [Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2), Point2D(1, 1, 3)]
        mesh = triangulate(points)
        skipped = getattr(mesh, 'skipped_points', [])
        self.assertEqual(len(skipped), 0)
        self.assertEqual(len(mesh.faces), 2)
        
        # Convert faces back to point tuples if needed for the test, or test faces directly
        triangles = [(mesh.vertices[f[0]], mesh.vertices[f[1]], mesh.vertices[f[2]]) for f in mesh.faces]
        vertex_ids = sorted(sorted(vertex.id for vertex in triangle) for triangle in triangles)
        self.assertIn(vertex_ids, [[[0, 1, 2], [1, 2, 3]], [[0, 1, 3], [0, 2, 3]]])

    def test_constrained_delaunay_preserves_domain_edges_and_area(self):
        outer = [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)]
        holes = [[Point2D(2, 2), Point2D(4, 2), Point2D(4, 4), Point2D(2, 4)]]
        triangles, constrained_edges = constrained_delaunay_triangulation(outer, holes)
        self.assertEqual(len(triangles), 8)
        self.assertGreaterEqual(len(constrained_edges), 8)

        covered_area = 0.0
        for a, b, c in triangles:
            covered_area += abs(
                (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0
            )
        self.assertAlmostEqual(covered_area, 32.0, places=6)

    def test_constrained_delaunay_is_locally_delaunay_on_unconstrained_edges(self):
        outer = [Point2D(0, 0), Point2D(5, 0), Point2D(5, 5), Point2D(0, 5)]
        triangles, constrained_edges = constrained_delaunay_triangulation(outer)

        def point_key(point):
            return (round(point.x, 6), round(point.y, 6), point.id)

        def edge_key(a, b):
            return tuple(sorted((point_key(a), point_key(b))))

        edge_map = {}
        for index, triangle in enumerate(triangles):
            for edge in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
                edge_map.setdefault(edge_key(*edge), []).append(index)

        for edge, owners in edge_map.items():
            if edge in constrained_edges or len(owners) != 2:
                continue
            first = triangles[owners[0]]
            second = triangles[owners[1]]
            shared = set(edge)
            a = next(vertex for vertex in first if point_key(vertex) not in shared)
            b = next(vertex for vertex in second if point_key(vertex) not in shared)
            shared_vertices = [vertex for vertex in first if point_key(vertex) in shared]
            c, d = shared_vertices
            self.assertLessEqual(incircle_sign(a, c, d, b), 0)


class MedialAxisTests(unittest.TestCase):
    def test_square_medial_axis_produces_interior_graph(self):
        polygon = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
        result = approximate_medial_axis(polygon, resolution=0.5)
        self.assertGreater(len(result["samples"]), 4)
        self.assertGreater(len(result["centers"]), 0)
        self.assertGreater(len(result["segments"]), 0)
        for start, end in result["segments"]:
            self.assertTrue(0.0 <= start.x <= 2.0 and 0.0 <= start.y <= 2.0)
            self.assertTrue(0.0 <= end.x <= 2.0 and 0.0 <= end.y <= 2.0)


if __name__ == "__main__":
    unittest.main()
