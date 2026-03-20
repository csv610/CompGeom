
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh import TriMesh

def test_from_triangles():
    p1, p2, p3, p4 = Point2D(0,0), Point2D(1,0), Point2D(0,1), Point2D(1,1)
    triangles = [(p1, p2, p3), (p2, p4, p3)]
    mesh = TriMesh.from_triangles(triangles)
    assert len(mesh.vertices) == 4
    assert len(mesh.faces) == 2

def test_betti_numbers_simple():
    # Single triangle: b0=1, b1=0, b2=0
    v = [Point2D(0,0), Point2D(1,0), Point2D(0,1)]
    m = TriMesh(v, [(0,1,2)])
    assert m.betti_numbers() == (1, 0, 0)

def test_betti_numbers_sphere():
    # Tetrahedron (sphere-like): b0=1, b1=0, b2=1
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    f = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
    m = TriMesh(v, f)
    assert m.betti_numbers() == (1, 0, 1)

def test_ensure_even_elements():
    # Start with 1 face (odd)
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)]
    m = TriMesh(v, [(0,1,2)])
    assert len(m.faces) == 1
    
    even_m = m.ensure_even_elements()
    assert len(even_m.faces) % 2 == 0
    assert len(even_m.faces) > 1

def test_flip_edge():
    # Two triangles sharing edge (1,2)
    v = [Point2D(0,0,0), Point2D(1,0,1), Point2D(0,1,2), Point2D(1,1,3)]
    # F0: (0,1,2), F1: (3,2,1)
    m = TriMesh(v, [(0,1,2), (3,2,1)])
    
    success = m.flip_edge(1, 2)
    assert success is True
    # Shared edge (1,2) should be replaced by (0,3)
    # Check that 1 and 2 are no longer in the same face? 
    # No, they will still be in the mesh, but faces changed.
    for f in m.faces:
        assert not (1 in f.v_indices and 2 in f.v_indices)
        assert (0 in f.v_indices and 3 in f.v_indices)

def test_flip_edge_invalid():
    v = [Point2D(0,0), Point2D(1,0), Point2D(0,1)]
    m = TriMesh(v, [(0,1,2)])
    # Only one face, no shared edge to flip
    assert m.flip_edge(0, 1) is False
