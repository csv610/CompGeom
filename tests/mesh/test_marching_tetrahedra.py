"""Unit tests for Marching Tetrahedra algorithm."""
import pytest
import numpy as np
from compgeom.mesh.volume.marching_tetrahedra import MarchingTetrahedra
from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh
from compgeom.kernel import Point3D

def test_marching_tetrahedra_single_tet():
    # A single tetrahedron with one vertex above isovalue
    nodes = [
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(0, 1, 0),
        Point3D(0, 0, 1)
    ]
    cells = [(0, 1, 2, 3)]
    mesh = TetMesh(nodes, cells)
    
    # Vertex 0 is above (1.0), others below (-1.0). Isovalue 0.0.
    node_values = np.array([1.0, -1.0, -1.0, -1.0])
    
    iso_mesh = MarchingTetrahedra.from_tetmesh(mesh, node_values, isovalue=0.0)
    
    # We expect 1 triangle and 3 vertices (midpoints of edges connected to vertex 0)
    assert len(iso_mesh.faces) == 1
    assert len(iso_mesh.vertices) == 3
    
    # Midpoints should be (0.5, 0, 0), (0, 0.5, 0), (0, 0, 0.5)
    expected_pts = { (0.5, 0, 0), (0, 0.5, 0), (0, 0, 0.5) }
    actual_pts = { (v.x, v.y, v.z) for v in iso_mesh.vertices }
    for p in expected_pts:
        assert any(np.allclose(p, a) for a in actual_pts)

def test_marching_tetrahedra_implicit_sphere():
    # Sphere of radius 0.5 at origin
    def sphere_sdf(x, y, z):
        return 0.5 - np.sqrt(x**2 + y**2 + z**2)
    
    bmin = (-1, -1, -1)
    bmax = (1, 1, 1)
    
    # Extract surface
    mesh = MarchingTetrahedra.from_implicit(sphere_sdf, bmin, bmax, resolution=10, isovalue=0.0)
    
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0
    
    # All vertices should be approximately at distance 0.5 from origin
    for v in mesh.vertices:
        dist = np.sqrt(v.x**2 + v.y**2 + v.z**2)
        assert pytest.approx(dist, abs=0.1) == 0.5
