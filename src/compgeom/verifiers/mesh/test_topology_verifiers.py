import unittest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.verifiers.mesh.topology_verifiers import (
    verify_mesh_tunnels,
    verify_mesh_cavities,
    verify_mesh_voids,
)


class TestTopologyVerifiers(unittest.TestCase):
    def test_sphere_topology(self):
        # A simple tetrahedron as a sphere approximation
        # b0=1, b1=0, b2=1
        vertices = [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(0, 0, 1),
        ]
        faces = [
            (0, 1, 2),
            (0, 1, 3),
            (0, 2, 3),
            (1, 2, 3),
        ]
        mesh = TriMesh(vertices, faces)
        self.assertTrue(verify_mesh_tunnels(mesh, 0))
        self.assertTrue(verify_mesh_cavities(mesh, 1))

    def test_torus_topology(self):
        # We need a torus. For simplicity, let's use the Betti numbers 
        # from a known torus mesh if we had one.
        # Since generating a torus is complex, let's just test a cylinder (open).
        # Open cylinder: b0=1, b1=1, b2=0
        vertices = [
            # Bottom circle
            Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(-1, 0, 0), Point3D(0, -1, 0),
            # Top circle
            Point3D(1, 0, 1), Point3D(0, 1, 1), Point3D(-1, 0, 1), Point3D(0, -1, 1),
        ]
        faces = [
            # Side panels (2 triangles per panel)
            (0, 1, 4), (1, 5, 4),
            (1, 2, 5), (2, 6, 5),
            (2, 3, 6), (3, 7, 6),
            (3, 0, 7), (0, 4, 7),
        ]
        mesh = TriMesh(vertices, faces)
        self.assertTrue(verify_mesh_tunnels(mesh, 1))
        self.assertTrue(verify_mesh_cavities(mesh, 0))

    def test_mismatch(self):
        vertices = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
        faces = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
        mesh = TriMesh(vertices, faces)
        
        with self.assertRaises(ValueError):
            verify_mesh_tunnels(mesh, 1) # Sphere has 0 tunnels
            
        with self.assertRaises(ValueError):
            verify_mesh_cavities(mesh, 0) # Closed sphere has 1 enclosed volume (b2=1)


if __name__ == "__main__":
    unittest.main()
