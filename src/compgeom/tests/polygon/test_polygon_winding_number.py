from compgeom.kernel import Point2D
from compgeom.mesh import PolygonMesh, PolygonWinding, point_winding_number


def test_point_winding_number_for_ccw_polygon():
    polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]

    assert point_winding_number(Point2D(2, 2), polygon) == 1
    assert point_winding_number(Point2D(5, 2), polygon) == 0


def test_point_winding_number_for_cw_polygon():
    polygon = [Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0)]

    assert point_winding_number(Point2D(2, 2), polygon) == -1
    assert point_winding_number(Point2D(5, 2), polygon) == 0


def test_point_winding_number_is_zero_in_concavity_outside_region():
    polygon = [
        Point2D(0, 0),
        Point2D(4, 0),
        Point2D(4, 4),
        Point2D(2, 2),
        Point2D(0, 4),
    ]

    assert point_winding_number(Point2D(1, 1), polygon) == 1
    assert point_winding_number(Point2D(2, 3), polygon) == 0


def test_point_winding_number_treats_boundary_as_nonzero():
    polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]

    assert point_winding_number(Point2D(0, 2), polygon) == 1
    assert point_winding_number(Point2D(0, 0), polygon) == 1


def test_polygon_winding_helper_reads_face_vertices_from_mesh():
    vertices = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4), Point2D(6, 0), Point2D(6, 2)]
    mesh = PolygonMesh(vertices, [(0, 1, 2, 3), (1, 4, 5)])

    assert PolygonWinding.winding_number(Point2D(2, 2), mesh, 0) == 1
    assert PolygonWinding.winding_number(Point2D(5, 1), mesh, 1) == 1
    assert PolygonWinding.winding_number(Point2D(5, 3), mesh, 1) == 0
