import unittest
from compgeom.mesh import TriMesh, MeshTopology
from compgeom.kernel import Point3D

class TestOrientability(unittest.TestCase):
    def test_orientable_cylinder(self):
        # 4 vertices on top circle, 4 on bottom circle
        pts = [
            Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(-1, 0, 0), Point3D(0, -1, 0), # Bottom
            Point3D(1, 0, 1), Point3D(0, 1, 1), Point3D(-1, 0, 1), Point3D(0, -1, 1)  # Top
        ]
        # Triangles for 4 sides (quads split into 2 tris)
        faces = [
            (0, 1, 5), (0, 5, 4), # Side 0
            (1, 2, 6), (1, 6, 5), # Side 1
            (2, 3, 7), (2, 7, 6), # Side 2
            (3, 0, 4), (3, 4, 7)  # Side 3
        ]
        mesh = TriMesh(pts, faces)
        self.assertTrue(MeshTopology(mesh).is_orientable())

    def test_non_orientable_mobius(self):
        # A simple 3-rectangle Mobius strip
        # pts 0-1, 2-3, 4-5, 0-1(flipped)
        pts = [
            Point3D(0, 0, 0), Point3D(0, 1, 0), # 0, 1
            Point3D(1, 0, 0), Point3D(1, 1, 0), # 2, 3
            Point3D(2, 0, 0), Point3D(2, 1, 0)  # 4, 5
        ]
        # Rect 1: (0,2,3,1) -> (0,2,3), (0,3,1)
        # Rect 2: (2,4,5,3) -> (2,4,5), (2,5,3)
        # Rect 3 (Twist): (4,1,0,5) -> (4,1,0), (4,0,5)
        faces = [
            (0, 2, 3), (0, 3, 1),
            (2, 4, 5), (2, 5, 3),
            (4, 1, 0), (4, 0, 5)
        ]
        mesh = TriMesh(pts, faces)
        self.assertFalse(MeshTopology(mesh).is_orientable())

if __name__ == "__main__":
    unittest.main()
