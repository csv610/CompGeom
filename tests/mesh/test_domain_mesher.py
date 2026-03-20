
import pytest
from compgeom.kernel import Point2D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.trimesh.domain_mesher import DomainMesher

def test_discretize_segment():
    p1, p2 = Point2D(0, 0), Point2D(10, 0)
    # segment_length = 3 -> 4 segments (0-3, 3-6, 6-9, 9-10) -> 5 points
    pts = DomainMesher._discretize_segment(p1, p2, 3.0)
    assert len(pts) == 5
    assert pts[0] == p1
    assert pts[-1] == p2

def test_generate_internal_points():
    boundary = [Point2D(0,0), Point2D(10,0), Point2D(10,10), Point2D(0,10)]
    pts = DomainMesher._generate_internal_points(boundary, 2.0, num_internal_points=10)
    assert len(pts) == 10
    for p in pts:
        assert 0 < p.x < 10
        assert 0 < p.y < 10

def test_mesh_square():
    # 10x10 square, boundary segments of length 5 (2 per edge)
    # Total boundary points: 4 corners + 4 midpoints = 8 unique
    mesh = DomainMesher.square(10.0, 5.0, num_internal_points=1)
    assert isinstance(mesh, TriMesh)
    assert len(mesh.vertices) >= 8
    assert len(mesh.faces) > 0

def test_mesh_rectangle():
    mesh = DomainMesher.rectangle(20.0, 10.0, 5.0, num_internal_points=2)
    assert len(mesh.vertices) >= 10
    assert len(mesh.faces) > 0

def test_mesh_triangle():
    mesh = DomainMesher.triangle(10.0, 5.0, num_internal_points=1)
    assert len(mesh.vertices) >= 6
    assert len(mesh.faces) > 0

def test_mesh_circle():
    # Circle radius 5, boundary segments length 5.
    # Circumference approx 31.4 -> ~7 segments.
    mesh = DomainMesher.circle(5.0, 5.0, num_internal_points=2)
    assert len(mesh.vertices) >= 8
    assert len(mesh.faces) > 0
