import unittest
import math
from compgeom.kernel import Point2D
from compgeom.algo.path import shortest_path

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

if __name__ == "__main__":
    unittest.main()
