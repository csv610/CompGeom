"""Tests for primitive mesh generation."""

import unittest
from compgeom.mesh.surfmesh.trimesh.primitives import Primitives

class TestPrimitives(unittest.TestCase):
    def test_sphere(self):
        mesh = Primitives.sphere(radius=1.0, subdivisions=2)
        self.assertTrue(len(mesh.vertices) > 0)
        self.assertTrue(len(mesh.faces) > 0)

    def test_ellipsoid(self):
        mesh = Primitives.ellipsoid(rx=1.0, ry=2.0, rz=0.5, subdivisions=2)
        self.assertTrue(len(mesh.vertices) > 0)
        self.assertTrue(len(mesh.faces) > 0)

    def test_oblate_spheroid(self):
        mesh = Primitives.oblate_spheroid(equatorial_radius=1.0, polar_radius=0.5, subdivisions=1)
        self.assertTrue(len(mesh.vertices) > 0)
        with self.assertRaises(ValueError):
            Primitives.oblate_spheroid(equatorial_radius=0.5, polar_radius=1.0)

    def test_prolate_spheroid(self):
        mesh = Primitives.prolate_spheroid(equatorial_radius=0.5, polar_radius=1.0, subdivisions=1)
        self.assertTrue(len(mesh.vertices) > 0)
        with self.assertRaises(ValueError):
            Primitives.prolate_spheroid(equatorial_radius=1.0, polar_radius=0.5)

    def test_torus(self):
        mesh = Primitives.torus(major_radius=1.0, minor_radius=0.3, major_segments=10, minor_segments=10)
        self.assertTrue(len(mesh.vertices) > 0)
        self.assertTrue(len(mesh.faces) > 0)

    def test_cube(self):
        mesh = Primitives.cube(size=1.0)
        self.assertEqual(len(mesh.vertices), 8)
        self.assertEqual(len(mesh.faces), 12)

    def test_cuboid(self):
        mesh = Primitives.cuboid(length=1.0, width=2.0, height=3.0)
        self.assertEqual(len(mesh.vertices), 8)
        self.assertEqual(len(mesh.faces), 12)

    def test_quad(self):
        mesh = Primitives.quad(width=1.0, height=2.0)
        self.assertEqual(len(mesh.vertices), 4)
        self.assertEqual(len(mesh.faces), 2)

    def test_polygon(self):
        segments = 16
        mesh = Primitives.polygon(radius=1.0, segments=segments)
        self.assertEqual(len(mesh.vertices), segments + 1)
        self.assertEqual(len(mesh.faces), segments)

    def test_cylinder(self):
        segments = 16
        mesh = Primitives.cylinder(radius=1.0, height=2.0, segments=segments)
        # vertices = bottom_cap (segments) + top_cap (segments) + 2 centers
        self.assertEqual(len(mesh.vertices), 2 * segments + 2)
        # faces = sides (2 * segments) + bottom_cap (segments) + top_cap (segments)
        self.assertEqual(len(mesh.faces), 4 * segments)

    def test_hexagonal_prism(self):
        mesh = Primitives.hexagonal_prism(radius=1.0, height=2.0)
        self.assertEqual(len(mesh.vertices), 2 * 6 + 2)
        self.assertEqual(len(mesh.faces), 4 * 6)

    def test_triangular_prism(self):
        mesh = Primitives.triangular_prism(radius=1.0, height=2.0)
        self.assertEqual(len(mesh.vertices), 2 * 3 + 2)
        self.assertEqual(len(mesh.faces), 4 * 3)

    def test_cone(self):
        segments = 16
        mesh = Primitives.cone(radius=1.0, height=2.0, segments=segments)
        # vertices = tip (1) + base (segments) + base center (1)
        self.assertEqual(len(mesh.vertices), segments + 2)
        # faces = sides (segments) + base (segments)
        self.assertEqual(len(mesh.faces), 2 * segments)

    def test_pyramid(self):
        mesh = Primitives.pyramid(base_size=1.0, height=2.0, base_segments=4)
        self.assertEqual(len(mesh.vertices), 4 + 2)
        self.assertEqual(len(mesh.faces), 2 * 4)

    def test_platonic_solids(self):
        self.assertEqual(len(Primitives.tetrahedron().vertices), 4)
        self.assertEqual(len(Primitives.octahedron().vertices), 6)
        self.assertEqual(len(Primitives.icosahedron().vertices), 12)
        self.assertEqual(len(Primitives.dodecahedron().vertices), 20)

if __name__ == "__main__":
    unittest.main()
