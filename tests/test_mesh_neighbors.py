import unittest
from compgeom.kernel import Point2D
from compgeom.mesh import mesh_neighbors

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

if __name__ == "__main__":
    unittest.main()
