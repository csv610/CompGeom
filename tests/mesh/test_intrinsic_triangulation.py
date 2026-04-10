"""Unit tests for Intrinsic Delaunay Triangulation."""
import pytest
import math
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.trimesh.intrinsic_triangulation import IntrinsicTriangulation
from compgeom.kernel import Point3D

def test_intrinsic_delaunay_flat_rectangle():
    # Two triangles forming a rectangle (0,0), (2,0), (2,1), (0,1)
    # Tri 1: (0,0), (2,0), (0,1)
    # Tri 2: (2,0), (2,1), (0,1)
    # Diagonal is (2,0)-(0,1), length sqrt(5) ~ 2.236
    # Angles opposite to diagonal: 
    # Tri 1: angle at (0,0) is 90 deg (pi/2)
    # Tri 2: angle at (2,1) is 90 deg (pi/2)
    # Sum = pi. It is JUST Delaunay.
    
    # Let's make it non-Delaunay by moving (0,0) and (2,1) closer.
    # Actually, simpler: make a diamond with a short diagonal.
    # P0=(0,0), P1=(1,-0.1), P2=(2,0), P3=(1,0.1)
    # Edges: (0,1,2) and (0,2,3). Diagonal 0-2 is long. 1-3 is short.
    # The sum of opposite angles for 0-2 will be > pi.
    
    verts = [
        Point3D(0, 0, 0),   # 0
        Point3D(1, -0.1, 0),# 1
        Point3D(2, 0, 0),   # 2
        Point3D(1, 0.1, 0)  # 3
    ]
    faces = [(0, 1, 2), (0, 2, 3)]
    mesh = TriMesh(verts, faces)
    
    it = IntrinsicTriangulation.from_mesh(mesh)
    
    # Initially, edge (0,2) is non-Delaunay
    # Find the edge (0,2)
    bad_he = None
    for he in it.he_mesh.edges:
        u, v = he.vertex.idx, he.next.vertex.idx
        if {u, v} == {0, 2}:
            bad_he = he
            break
    
    assert bad_he is not None
    assert not it.is_delaunay(bad_he)
    
    # Make Delaunay
    it.make_delaunay()
    
    # After flip, the faces should be (0,1,3) and (1,2,3) or similar
    final_mesh = it.to_mesh()
    assert len(final_mesh.faces) == 2
    
    # Check if (0,2) is still a face edge. It shouldn't be.
    for f in final_mesh.faces:
        assert set(f) != {0, 1, 2}
        assert set(f) != {0, 2, 3}
        
    # The new faces should involve edge (1,3)
    found_new_edge = False
    for f in final_mesh.faces:
        if {1, 3}.issubset(set(f)):
            found_new_edge = True
    assert found_new_edge

def test_intrinsic_delaunay_on_sphere():
    # A simple mesh on a sphere or highly curved surface
    # For now, just verify it doesn't crash and maintains manifoldness.
    from compgeom.mesh.surface.surface_mesh import SurfaceMesh
    
    # Regular Tetrahedron (not Delaunay? No, it should be)
    # Let's use a "squashed" tetrahedron
    verts = [
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0.5, 0.5, 0.1)
    ]
    faces = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    mesh = TriMesh(verts, faces)
    
    it = IntrinsicTriangulation.from_mesh(mesh)
    it.make_delaunay()
    
    final = it.to_mesh()
    assert len(final.vertices) == 4
    assert len(final.faces) == 4
