
import unittest
import math
from compgeom.mesh import TriangleMesh
from compgeom.kernel import Point3D
from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
from compgeom.mesh.surfmesh.trimesh.primitives import Primitives

# Import functions from our task script
from .sphere_projection_task import (
    calculate_sphere_radius,
    project_to_sphere,
    is_mesh_valid_on_sphere,
    as_rigid_as_possible,
    as_conformal_as_possible
)

class TestSphereProjection(unittest.TestCase):
    def setUp(self):
        # Create a small ellipsoid for testing
        self.rx, self.ry, self.rz = 2.0, 1.0, 1.0
        self.mesh = Primitives.ellipsoid(rx=self.rx, ry=self.ry, rz=self.rz, subdivisions=1)
        # Fix orientation to CCW
        new_faces = [(f[0], f[2], f[1]) for f in self.mesh.faces]
        self.mesh = TriangleMesh(self.mesh.vertices, new_faces)
        self.com = MeshAnalysis.center_of_mass(self.mesh)
        self.area = MeshAnalysis.total_area(self.mesh)
        self.radius = calculate_sphere_radius(self.area)

    def test_radius_calculation(self):
        # Area = 4 * pi * r^2
        expected_r = 1.0
        area = 4 * math.pi
        self.assertAlmostEqual(calculate_sphere_radius(area), expected_r)
        
        expected_r = 5.0
        area = 4 * math.pi * 25
        self.assertAlmostEqual(calculate_sphere_radius(area), expected_r)

    def test_projection_distance(self):
        spherical_mesh = project_to_sphere(self.mesh, self.com, self.radius)
        for v in spherical_mesh.vertices:
            dist = math.sqrt((v.x - self.com[0])**2 + (v.y - self.com[1])**2 + (getattr(v, 'z', 0.0) - self.com[2])**2)
            self.assertAlmostEqual(dist, self.radius, places=5)

    def test_validity_check(self):
        # A sphere should be valid
        sphere = Primitives.sphere(radius=self.radius, subdivisions=1)
        # Fix orientation if needed (check one face)
        v0, v1, v2 = [sphere.vertices[i] for i in sphere.faces[0]]
        # Simple outward check
        nx = (v1.y-v0.y)*v2.z - (v1.z-v0.z)*v2.y # partial cross
        # Just use our robust check
        center = (0,0,0)
        
        # If sphere is CW, reverse it
        if not is_mesh_valid_on_sphere(sphere, center):
            sphere = TriangleMesh(sphere.vertices, [(f[0], f[2], f[1]) for f in sphere.faces])
            
        self.assertTrue(is_mesh_valid_on_sphere(sphere, center))
        
        # An inverted sphere should be invalid
        inverted_faces = [(f[0], f[2], f[1]) for f in sphere.faces]
        inverted_sphere = TriangleMesh(sphere.vertices, inverted_faces)
        self.assertFalse(is_mesh_valid_on_sphere(inverted_sphere, center))

    def test_optimization_runs(self):
        # Test that ARAP and ACAP run without errors and maintain vertex count
        spherical_mesh = project_to_sphere(self.mesh, self.com, self.radius)
        
        arap_mesh = as_rigid_as_possible(spherical_mesh, self.mesh, self.com, self.radius, iterations=5)
        self.assertEqual(len(arap_mesh.vertices), len(self.mesh.vertices))
        self.assertEqual(len(arap_mesh.faces), len(self.mesh.faces))
        
        acap_mesh = as_conformal_as_possible(spherical_mesh, self.mesh, self.com, self.radius, iterations=5)
        self.assertEqual(len(acap_mesh.vertices), len(self.mesh.vertices))
        self.assertEqual(len(acap_mesh.faces), len(self.mesh.faces))

    def test_topological_preservation(self):
        spherical_mesh = project_to_sphere(self.mesh, self.com, self.radius)
        self.assertEqual(list(spherical_mesh.faces), list(self.mesh.faces))

if __name__ == "__main__":
    unittest.main()
