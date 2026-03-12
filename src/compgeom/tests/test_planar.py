import pytest
from compgeom.kernel import Point
from compgeom.polygon.planar import build_polygon_dcel, face_contains_point, locate_face

def test_build_polygon_dcel_basic():
    # Simple square
    poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    dcel = build_polygon_dcel(poly)
    assert len(dcel.vertices) == 4
    # Wait, _link_cycle creates 4 vertices, 4 interior edges, 4 exterior edges.
    # Total vertices = 4.
    # Total half-edges = 8.
    # Total faces = 2 (bounded and exterior).
    assert len(dcel.vertices) == 4
    assert len(dcel.half_edges) == 8
    assert len(dcel.faces) == 2

def test_face_contains_point():
    poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    dcel = build_polygon_dcel(poly)
    bounded_face = dcel.faces[0]
    assert face_contains_point(bounded_face, Point(0.5, 0.5)) is True
    assert face_contains_point(bounded_face, Point(1.5, 0.5)) is False

def test_locate_face():
    poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    dcel = build_polygon_dcel(poly)
    face = locate_face(dcel, Point(0.5, 0.5))
    assert face.id == 0
    assert face.is_exterior is False
    
    face_ext = locate_face(dcel, Point(2, 2))
    assert face_ext.is_exterior is True

def test_build_polygon_dcel_with_hole():
    outer = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
    hole = [Point(4, 4), Point(4, 6), Point(6, 6), Point(6, 4)]
    dcel = build_polygon_dcel(outer, holes=[hole])
    assert len(dcel.vertices) == 8
    assert len(dcel.faces) == 2 # Bounded face and exterior face.
    # Wait, build_polygon_dcel adds hole exterior to bounded_face inner_components.
    assert len(dcel.faces[0].inner_components) == 1
    
    # Point inside the hole should be in the exterior face
    face = locate_face(dcel, Point(5, 5))
    assert face.is_exterior is True
