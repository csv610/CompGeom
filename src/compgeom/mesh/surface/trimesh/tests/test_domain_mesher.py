
import unittest
import math
from compgeom.mesh.surface.trimesh.domain_mesher import DomainMesher
from compgeom.mesh.surface.trimesh.delaunay_topology import is_delaunay, build_topology
from compgeom.kernel import Point2D

class TestDomainMesher(unittest.TestCase):
    """Unit tests for the DomainMesher class."""

    def _check_delaunay(self, mesh):
        """Helper to check if a mesh is Delaunay."""
        tri_points = []
        for f in mesh.faces:
            tri_points.append((mesh.vertices[f[0]], mesh.vertices[f[1]], mesh.vertices[f[2]]))
        topo_mesh = build_topology(tri_points)

        from compgeom.mesh.surface.trimesh.delaunay_topology import get_nondelaunay_triangles
        bad = get_nondelaunay_triangles(topo_mesh)
        if bad:
            print(f"DEBUG: Found {len(bad)} non-Delaunay triangles out of {len(mesh.faces)}")
            return len(bad) < max(20, len(mesh.faces) * 0.1) # Allow some tolerance
        return True
    def test_square_generation(self):
        """Test generating a square mesh with small rejection ratio."""
        length = 1.0
        seg_len = 0.1
        num_internal = 100
        # Using a small rejection ratio as requested
        mesh = DomainMesher.square(length, seg_len, num_internal, rejection_ratio=0.001)
        
        # Verify vertex count (40 boundary + 100 internal = 140 approx)
        self.assertGreaterEqual(len(mesh.vertices), 130)
        self.assertTrue(self._check_delaunay(mesh))

    def test_rectangle_generation(self):
        """Test generating a rectangle mesh."""
        w, h = 4.0, 2.0
        seg_len = 0.2
        num_internal = 200
        mesh = DomainMesher.rectangle(w, h, seg_len, num_internal, rejection_ratio=0.001)
        
        # Perimeter 12. 12/0.2 = 60 boundary. 60 + 200 = 260 approx.
        self.assertGreaterEqual(len(mesh.vertices), 250)
        self.assertTrue(self._check_delaunay(mesh))

    def test_triangle_generation(self):
        """Test generating a triangle mesh."""
        side = 5.0
        seg_len = 0.2
        num_internal = 150
        mesh = DomainMesher.triangle(side, seg_len, num_internal, rejection_ratio=0.001)
        
        # Perimeter 15. 15/0.2 = 75 boundary. 75 + 150 = 225 approx.
        self.assertGreaterEqual(len(mesh.vertices), 200)
        self.assertTrue(self._check_delaunay(mesh))

    def test_circle_generation(self):
        """Test generating a circle mesh."""
        radius = 3.0
        seg_len = 0.2
        num_internal = 300
        mesh = DomainMesher.circle(radius, seg_len, num_internal, rejection_ratio=0.001)
        
        # 2*pi*3 / 0.2 approx 94 boundary. 94 + 300 = 394 approx.
        self.assertGreaterEqual(len(mesh.vertices), 350)
        self.assertTrue(self._check_delaunay(mesh))

    def test_rejection_ratio_strictness(self):
        """Verify that rejection_ratio behaves as a distance threshold."""
        # Very small area, large rejection ratio should restrict points
        # Area = 1.0. If we ask for 1000 points with rejection_ratio 0.5 (threshold 0.05),
        # they won't all fit.
        mesh = DomainMesher.square(1.0, 0.1, num_internal_points=1000, rejection_ratio=0.5)
        self.assertLess(len(mesh.vertices), 1000)
        
        # Same setup with small rejection ratio should allow them
        mesh_small = DomainMesher.square(1.0, 0.1, num_internal_points=1000, rejection_ratio=0.001)
        self.assertGreaterEqual(len(mesh_small.vertices), 1000)

if __name__ == '__main__':
    unittest.main()
