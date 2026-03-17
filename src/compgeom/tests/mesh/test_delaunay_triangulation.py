from compgeom.kernel import Point2D, orientation_sign
from compgeom.mesh.surfmesh.trimesh.delaunay_triangulation import build_topology, is_delaunay, DelaunayMesher


def test_delaunay_flip_preserves_ccw_direction_for_new_triangles():
    a = Point2D(0, 1, id=1)
    b = Point2D(0, 0, id=2)
    c = Point2D(1, 0, id=3)
    d = Point2D(0.5, -0.1, id=4)

    mesh = build_topology([(a, b, c), (d, c, b)])

    DelaunayMesher.delaunay_flip(mesh)

    assert is_delaunay(mesh) is True
    assert {frozenset(triangle.vertices) for triangle in mesh} == {
        frozenset((a, b, d)),
        frozenset((a, c, d)),
    }
    for triangle in mesh:
        assert orientation_sign(*triangle.vertices) >= 0
