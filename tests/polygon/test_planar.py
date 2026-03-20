import pytest
from compgeom.kernel import Point2D
from compgeom.polygon.planar import DCEL

def test_build_polygon_dcel_basic():
    # Simple square
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    dcel = DCEL.from_polygon(poly)
    assert len(dcel.vertices) == 4
    # Total half-edges = 8.
    # Total faces = 2 (bounded and exterior).
    assert len(dcel.vertices) == 4
    assert len(dcel.half_edges) == 8
    assert len(dcel.faces) == 2

def test_face_contains_point():
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    dcel = DCEL.from_polygon(poly)
    bounded_face = dcel.faces[0]
    assert bounded_face.contains_point(Point2D(0.5, 0.5)) is True
    assert bounded_face.contains_point(Point2D(1.5, 0.5)) is False

def test_locate_face():
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    dcel = DCEL.from_polygon(poly)
    face = dcel.locate_face(Point2D(0.5, 0.5))
    assert face.id == 0
    assert face.is_exterior is False
    
    face_ext = dcel.locate_face(Point2D(2, 2))
    assert face_ext.is_exterior is True

def test_build_polygon_dcel_with_hole():
    outer = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    hole = [Point2D(4, 4), Point2D(4, 6), Point2D(6, 6), Point2D(6, 4)]
    dcel = DCEL.from_polygon(outer, holes=[hole])
    assert len(dcel.vertices) == 8
    assert len(dcel.faces) == 2 # Bounded face and exterior face.
    assert len(dcel.faces[0].inner_components) == 1
    
    # Point inside the hole should be in the exterior face
    face = dcel.locate_face(Point2D(5, 5))
    assert face.is_exterior is True
