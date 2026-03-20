
import pytest
import math
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.edge_mesh import EdgeMesh

def test_edge_mesh_2d():
    p1 = Point2D(0, 0)
    p2 = Point2D(10, 0)
    p3 = Point2D(0, 10)
    # 3 segments forming a triangle
    segments = [(p1, p2), (p2, p3), (p3, p1)]
    
    em = EdgeMesh.from_segments(segments)
    assert len(em.vertices) == 3
    assert len(em.edges) == 3
    
    expected_len = 10 + 10 + math.sqrt(200)
    assert em.total_length() == pytest.approx(expected_len)
    assert em.euler_characteristic() == 0 # 3 - 3 = 0

def test_edge_mesh_3d():
    p1 = Point3D(0, 0, 0)
    p2 = Point3D(1, 0, 0)
    # 1 segment
    em = EdgeMesh.from_segments([(p1, p2)])
    assert em.total_length() == pytest.approx(1.0)
    assert em.euler_characteristic() == 1 # 2 - 1 = 1

def test_edge_mesh_manual_init():
    v = [Point2D(0,0), Point2D(1,1)]
    e = [(0, 1)]
    em = EdgeMesh(v, e)
    assert em.total_length() == pytest.approx(math.sqrt(2))
