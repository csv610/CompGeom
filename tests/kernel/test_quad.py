
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.kernel import quad

def test_area():
    """Tests the area function for a simple square."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
    assert quad.area(p1, p4, p3, p2) == pytest.approx(1.0) # Clockwise
    assert quad.area(p1, p2, p3, p4) == pytest.approx(1.0) # Counter-clockwise

def test_area_concave():
    """Tests the area of a concave quad (arrowhead)."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(2, 0), Point2D(1, 1), Point2D(0, 2)
    assert quad.area(p1, p2, p3, p4) == pytest.approx(2.0)


def test_is_convex():
    """Tests the is_convex function."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
    assert quad.is_convex(p1, p2, p3, p4) is True
    p1_concave, p2_concave, p3_concave, p4_concave = Point2D(0, 0), Point2D(2, 0), Point2D(1, -1), Point2D(0, 2)
    assert quad.is_convex(p1_concave, p2_concave, p3_concave, p4_concave) is False

def test_split_to_triangles():
    """Tests splitting a quad into two triangles."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
    triangles = quad.split_to_triangles(p1, p2, p3, p4)
    assert triangles == [(p1, p2, p3), (p1, p3, p4)]

def test_centroid():
    """Tests the centroid calculation."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)
    centroid = quad.centroid(p1, p2, p3, p4)
    assert centroid.x == pytest.approx(1.0)
    assert centroid.y == pytest.approx(1.0)

def test_is_planar():
    """Tests the is_planar function."""
    p1_2d, p2_2d, p3_2d, p4_2d = Point2D(0,0), Point2D(1,0), Point2D(1,1), Point2D(0,1)
    assert quad.is_planar(p1_2d, p2_2d, p3_2d, p4_2d) is True

    p1_3d, p2_3d, p3_3d, p4_3d = Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)
    assert quad.is_planar(p1_3d, p2_3d, p3_3d, p4_3d) is True
    
    p4_3d_nonplanar = Point3D(0, 1, 1)
    assert quad.is_planar(p1_3d, p2_3d, p3_3d, p4_3d_nonplanar) is False
    
    assert quad.is_planar(p1_2d, p2_2d, p3_3d, p4_3d) is True

def test_is_cyclic():
    """Tests the is_cyclic function."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(0, 1)
    assert quad.is_cyclic(p1, p2, p3, p4) is True
    
    p4_noncyclic = Point2D(0, 1.5)
    assert quad.is_cyclic(p1, p2, p3, p4_noncyclic) is False
    
    p1_3d, p2_3d, p3_3d = Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0)
    p4_3d_nonplanar = Point3D(0, 1, 1)
    assert quad.is_cyclic(p1_3d, p2_3d, p3_3d, p4_3d_nonplanar) is False

def test_barycentric_coords():
    """Tests barycentric coordinate calculation."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
    
    # Test center point
    p_center = Point2D(0.5, 0.5)
    u, v = quad.barycentric_coords(p_center, p1, p2, p3, p4)
    assert u == pytest.approx(0.5)
    assert v == pytest.approx(0.5)
    
    # Test a vertex
    u, v = quad.barycentric_coords(p1, p1, p2, p3, p4)
    assert u == pytest.approx(0.0)
    assert v == pytest.approx(0.0)

def test_min_circle():
    """Tests the min_circle function."""
    p1, p2, p3, p4 = Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
    circle = quad.min_circle(p1, p2, p3, p4)
    assert circle.center.x == pytest.approx(0.5)
    assert circle.center.y == pytest.approx(0.5)
    assert circle.radius == pytest.approx((2**0.5) / 2)

    p1_tri, p2_tri, p3_tri, p4_tri = Point2D(-1, 0), Point2D(1, 0), Point2D(0, 1), Point2D(0, 0.1)
    circle = quad.min_circle(p1_tri, p2_tri, p3_tri, p4_tri)
    assert circle.center.x == pytest.approx(0)
    assert circle.center.y == pytest.approx(0)
    assert circle.radius == pytest.approx(1.0)
