
import pytest
from compgeom.kernel import Point2D
from compgeom.algo import path

@pytest.fixture
def simple_mesh():
    # A 1x1 square divided into two triangles
    # Triangle 1: (0,0), (1,0), (1,1)
    # Triangle 2: (0,0), (1,1), (0,1)
    p1 = Point2D(0, 0, id=0)
    p2 = Point2D(1, 0, id=1)
    p3 = Point2D(1, 1, id=2)
    p4 = Point2D(0, 1, id=3)
    return [
        (p1, p2, p3),
        (p1, p3, p4)
    ]

def test_point_in_mesh(simple_mesh):
    assert path.point_in_mesh(simple_mesh, Point2D(0.5, 0.5)) is True
    assert path.point_in_mesh(simple_mesh, Point2D(1.5, 0.5)) is False
    assert path.point_in_mesh(simple_mesh, Point2D(0, 0)) is True

def test_boundary_edges(simple_mesh):
    edges = path.boundary_edges(simple_mesh)
    assert len(edges) == 4
    # Edges: (0,1), (1,2), (2,3), (3,0). Edge (0,2) is shared.
    ids = {tuple(sorted((e[0].id, e[1].id))) for e in edges}
    assert (0, 1) in ids
    assert (1, 2) in ids
    assert (2, 3) in ids
    assert (0, 3) in ids
    assert (0, 2) not in ids

def test_edge_shortest_path(simple_mesh):
    source = Point2D(0, 0, id=0)
    target = Point2D(1, 1, id=2)
    
    # Path along edges (0,0) -> (1,1) is direct diagonal edge (0,2)
    res_path, length = path.edge_shortest_path(simple_mesh, source, target)
    assert length == pytest.approx(2**0.5)
    assert res_path[0] == source
    assert res_path[-1] == target

    # Path from (1,0) to (0,1) should go through (0,0) or (1,1)
    # (1,0) -> (0,0) -> (0,1) length 2
    s2 = Point2D(1, 0, id=1)
    t2 = Point2D(0, 1, id=3)
    res_path2, length2 = path.edge_shortest_path(simple_mesh, s2, t2)
    assert length2 == pytest.approx(2.0)
    assert res_path2[0] == s2
    assert res_path2[-1] == t2

def test_true_shortest_path(simple_mesh):
    # In a convex mesh, true shortest path is always a straight line
    source = Point2D(0.1, 0.1)
    target = Point2D(0.9, 0.9)
    res_path, length = path.true_shortest_path(simple_mesh, source, target)
    assert length == pytest.approx(((0.8)**2 + (0.8)**2)**0.5)
    assert len(res_path) == 2

def test_shortest_path_wrapper(simple_mesh):
    s = Point2D(0, 0, id=0)
    t = Point2D(1, 1, id=2)
    
    p1, l1 = path.shortest_path(simple_mesh, s, t, mode="true")
    p2, l2 = path.shortest_path(simple_mesh, s, t, mode="edges")
    
    assert l1 == l2 # For diagonal edge they should be same
    
    with pytest.raises(ValueError):
        path.shortest_path(simple_mesh, s, t, mode="invalid")

def test_errors(simple_mesh):
    outside = Point2D(2, 2)
    inside = Point2D(0.5, 0.5)
    
    with pytest.raises(ValueError, match="Source point is outside the mesh."):
        path.shortest_path(simple_mesh, outside, inside)
    
    with pytest.raises(ValueError, match="Target point is outside the mesh."):
        path.shortest_path(simple_mesh, inside, outside)

def test_dijkstra_no_path():
    graph = {0: [(1, 1.0)]}
    p, d = path.dijkstra(graph, 0, 2)
    assert p is None
    assert d == float("inf")
