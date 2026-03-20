"""Tests for vertex movement constraints."""

import unittest
import math
from compgeom.kernel import Point3D
from compgeom.mesh.surface.node_move_constraints import VertexConstraint

class TestVertexConstraint(unittest.TestCase):
    def test_project_to_line(self):
        p = Point3D(1.0, 1.0, 1.0, id=0)
        start = Point3D(0.0, 0.0, 0.0)
        end = Point3D(1.0, 0.0, 0.0)
        
        projected = VertexConstraint.project_to_line(p, start, end)
        self.assertEqual(projected.x, 1.0)
        self.assertEqual(projected.y, 0.0)
        self.assertEqual(projected.z, 0.0)
        self.assertEqual(projected.id, 0)

    def test_project_to_sphere(self):
        p = Point3D(2.0, 0.0, 0.0, id=1)
        center = Point3D(0.0, 0.0, 0.0)
        radius = 1.0
        
        projected = VertexConstraint.project_to_sphere(p, center, radius)
        self.assertEqual(projected.x, 1.0)
        self.assertEqual(projected.y, 0.0)
        self.assertEqual(projected.z, 0.0)
        self.assertEqual(projected.id, 1)

    def test_project_to_cuboid(self):
        # Point outside
        p = Point3D(2.0, 0.5, 0.5, id=2)
        min_c = Point3D(0.0, 0.0, 0.0)
        max_c = Point3D(1.0, 1.0, 1.0)
        
        projected = VertexConstraint.project_to_cuboid(p, min_c, max_c)
        self.assertEqual(projected.x, 1.0)
        self.assertEqual(projected.y, 0.5)
        self.assertEqual(projected.z, 0.5)
        
        # Point inside, should snap to nearest face
        p_in = Point3D(0.9, 0.5, 0.5, id=3)
        projected_in = VertexConstraint.project_to_cuboid(p_in, min_c, max_c)
        self.assertEqual(projected_in.x, 1.0)
        self.assertEqual(projected_in.y, 0.5)
        self.assertEqual(projected_in.z, 0.5)

    def test_project_to_cylinder(self):
        p = Point3D(2.0, 0.0, 0.5, id=4) # Outside side
        bottom = Point3D(0.0, 0.0, 0.0)
        top = Point3D(0.0, 0.0, 1.0)
        radius = 1.0
        
        projected = VertexConstraint.project_to_cylinder(p, bottom, top, radius)
        self.assertAlmostEqual(projected.x, 1.0)
        self.assertAlmostEqual(projected.y, 0.0)
        self.assertAlmostEqual(projected.z, 0.5)

    def test_project_to_mesh(self):
        from compgeom.mesh.surface.primitives import Primitives
        mesh = Primitives.tetrahedron(size=2.0)
        p = Point3D(5.0, 5.0, 5.0, id=5)
        
        projected = VertexConstraint.project_to_mesh(p, mesh)
        # Should be some point on the tetrahedron
        dist_sq = (p.x - projected.x)**2 + (p.y - projected.y)**2 + (p.z - projected.z)**2
        self.assertTrue(dist_sq > 0)
        self.assertEqual(projected.id, 5)

if __name__ == "__main__":
    unittest.main()
