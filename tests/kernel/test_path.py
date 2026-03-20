import pytest
from compgeom.kernel import Point2D, distance
from compgeom.algo.path import (
    shortest_path, 
    point_in_mesh, 
    boundary_edges,
    edge_shortest_path,
    true_shortest_path
)

@pytest.fixture
def simple_mesh():
    # Two triangles forming a square: (0,0), (1,0), (1,1) and (0,0), (1,1), (0,1)
    p1 = Point2D(0, 0, id=1)
    p2 = Point2D(1, 0, id=2)
    p3 = Point2D(1, 1, id=3)
    p4 = Point2D(0, 1, id=4)
    return [(p1, p2, p3), (p1, p3, p4)]

def test_point_in_mesh(simple_mesh):
    assert point_in_mesh(simple_mesh, Point2D(0.5, 0.5)) is True
    assert point_in_mesh(simple_mesh, Point2D(1.5, 0.5)) is False

def test_boundary_edges(simple_mesh):
    edges = boundary_edges(simple_mesh)
    # Square has 4 boundary edges
    assert len(edges) == 4

def test_shortest_path_edges(simple_mesh):
    source = Point2D(0, 0, id=1)
    target = Point2D(1, 1, id=3)
    path, length = shortest_path(simple_mesh, source, target, mode="edges")
    assert length == pytest.approx(1.41421356)
    # It might return [source, vertex_at_0_0, target] because source is attached to the vertex
    assert len(path) >= 2
    assert path[0] == source
    assert path[-1] == target

def test_shortest_path_true(simple_mesh):
    source = Point2D(0, 0, id=1)
    target = Point2D(1, 1, id=3)
    path, length = shortest_path(simple_mesh, source, target, mode="true")
    assert length == pytest.approx(1.41421356)
    assert len(path) >= 2

def test_shortest_path_invalid_mode(simple_mesh):
    with pytest.raises(ValueError, match="Unsupported path mode"):
        shortest_path(simple_mesh, Point2D(0,0), Point2D(1,1), mode="invalid")

def test_shortest_path_outside_mesh(simple_mesh):
    with pytest.raises(ValueError, match="Source point is outside the mesh"):
        shortest_path(simple_mesh, Point2D(-1, -1), Point2D(1, 1))

def test_edge_shortest_path_on_edge(simple_mesh):
    # Point on edge (0,0)-(1,0)
    source = Point2D(0.5, 0, id=100)
    target = Point2D(1, 1, id=3)
    path, length = edge_shortest_path(simple_mesh, source, target)
    assert length > 0

def test_true_shortest_path_complex():
    # L-shape mesh to force non-direct path
    p1 = Point2D(0, 0, id=1)
    p2 = Point2D(5, 0, id=2)
    p3 = Point2D(5, 1, id=3)
    p4 = Point2D(1, 1, id=4)
    p5 = Point2D(1, 5, id=5)
    p6 = Point2D(0, 5, id=6)
    
    mesh = [
        (p1, p2, p4), (p2, p3, p4), # horizontal part
        (p1, p4, p6), (p4, p5, p6)  # vertical part
    ]
    source = Point2D(4.5, 0.5, id=10)
    target = Point2D(0.5, 4.5, id=11)
    
    path, length = true_shortest_path(mesh, source, target)
    assert length > distance(source, target)
    # Should go near p4 (1,1)
    assert any(p.x == 1 and p.y == 1 for p in path)
