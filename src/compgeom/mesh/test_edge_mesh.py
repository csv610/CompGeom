import math
import unittest
from compgeom.mesh.edge_mesh import EdgeMesh
from compgeom.kernel import Point2D, Point3D

class TestEdgeMesh(unittest.TestCase):
    def test_edge_mesh_2d(self):
        p0 = Point2D(0, 0)
        p1 = Point2D(1, 0)
        p2 = Point2D(1, 1)
        
        vertices = [p0, p1, p2]
        edges = [(0, 1), (1, 2)]
        
        mesh = EdgeMesh(vertices, edges)
        self.assertEqual(len(mesh.vertices), 3)
        self.assertEqual(len(mesh.edges), 2)
        self.assertAlmostEqual(mesh.total_length(), 2.0)
        self.assertEqual(mesh.euler_characteristic(), 1) # 3 vertices - 2 edges = 1

    def test_edge_mesh_3d(self):
        p0 = Point3D(0, 0, 0)
        p1 = Point3D(1, 1, 1)
        
        vertices = [p0, p1]
        edges = [(0, 1)]
        
        mesh = EdgeMesh(vertices, edges)
        self.assertEqual(len(mesh.vertices), 2)
        self.assertEqual(len(mesh.edges), 1)
        self.assertAlmostEqual(mesh.total_length(), math.sqrt(3))
        self.assertEqual(mesh.euler_characteristic(), 1) # 2 - 1 = 1

    def test_from_segments(self):
        p0 = Point2D(0, 0)
        p1 = Point2D(1, 0)
        p2 = Point2D(1, 1)
        
        segments = [(p0, p1), (p1, p2), (p2, p0)]
        mesh = EdgeMesh.from_segments(segments)
        
        self.assertEqual(len(mesh.vertices), 3)
        self.assertEqual(len(mesh.edges), 3)
        self.assertAlmostEqual(mesh.total_length(), 2.0 + math.sqrt(2))
        self.assertEqual(mesh.euler_characteristic(), 0) # 3 - 3 = 0 (closed loop)

if __name__ == "__main__":
    unittest.main()
