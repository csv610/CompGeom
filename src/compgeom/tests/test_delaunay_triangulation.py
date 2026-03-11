from compgeom.kernel import Point, orientation_sign
from compgeom.mesh.delaunay_triangulation import build_topology, is_delaunay, DelaunayMesher


def test_delaunay_flip_preserves_ccw_direction_for_new_triangles():
    a = Point(0, 1, id=1)
    b = Point(0, 0, id=2)
    c = Point(1, 0, id=3)
    d = Point(0.5, -0.1, id=4)

    mesh = build_topology([(a, b, c), (d, c, b)])

    DelaunayMesher.delaunay_flip(mesh)

    assert is_delaunay(mesh) is True
    assert {frozenset(triangle.vertices) for triangle in mesh} == {
        frozenset((a, b, d)),
        frozenset((a, c, d)),
    }
    for triangle in mesh:
        assert orientation_sign(*triangle.vertices) >= 0
