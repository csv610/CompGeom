from compgeom.kernel import Point2D, Point3D
from compgeom.kernel.predicates import orient2d, orient3d, incircle, insphere

# --- Tests for orient2d ---


def test_orient2d_ccw():
    """Tests a simple counter-clockwise case."""
    a = Point2D(0, 0)
    b = Point2D(1, 0)
    c = Point2D(1, 1)
    assert orient2d(a, b, c) == 1


def test_orient2d_cw():
    """Tests a simple clockwise case."""
    a = Point2D(0, 0)
    b = Point2D(1, 1)
    c = Point2D(1, 0)
    assert orient2d(a, b, c) == -1


def test_orient2d_collinear():
    """Tests a simple collinear case."""
    a = Point2D(0, 0)
    b = Point2D(1, 0)
    c = Point2D(2, 0)
    assert orient2d(a, b, c) == 0


def test_orient2d_collinear_vertical():
    """Tests a vertical collinear case."""
    a = Point2D(0, 0)
    b = Point2D(0, 1)
    c = Point2D(0, 2)
    assert orient2d(a, b, c) == 0


def test_orient2d_collinear_diagonal():
    """Tests a diagonal collinear case."""
    a = Point2D(0, 0)
    b = Point2D(1, 1)
    c = Point2D(2, 2)
    assert orient2d(a, b, c) == 0


def test_orient2d_degenerate_points():
    """Tests when all points are the same."""
    a = Point2D(1, 1)
    assert orient2d(a, a, a) == 0


def test_orient2d_two_points_same():
    """Tests when two points are the same."""
    a = Point2D(0, 0)
    b = Point2D(1, 1)
    assert orient2d(a, b, a) == 0
    assert orient2d(a, a, b) == 0
    assert orient2d(b, a, a) == 0


def test_orient2d_large_coordinates():
    """Tests with large coordinates that might cause precision issues."""
    a = Point2D(1e12, 1e12)
    b = Point2D(1e12 + 1, 1e12)
    c = Point2D(1e12 + 1, 1e12 + 1)
    assert orient2d(a, b, c) == 1


def test_orient2d_small_coordinates():
    """Tests with very small coordinates."""
    a = Point2D(0, 0)
    b = Point2D(1e-12, 0)
    c = Point2D(1e-12, 1e-12)
    assert orient2d(a, b, c) == 1


def test_orient2d_almost_collinear_ccw():
    """Tests a case that is very close to collinear but is CCW."""
    a = Point2D(0, 0)
    b = Point2D(1000, 0)
    c = Point2D(2000, 1e-9)
    assert orient2d(a, b, c) == 1


def test_orient2d_almost_collinear_cw():
    """Tests a case that is very close to collinear but is CW."""
    a = Point2D(0, 0)
    b = Point2D(1000, 0)
    c = Point2D(2000, -1e-9)
    assert orient2d(a, b, c) == -1


# --- Tests for orient3d ---


def test_orient3d_below():
    """Tests a simple case where d is below the plane abc."""
    a = Point3D(0, 0, 0)
    b = Point3D(1, 0, 0)
    c = Point3D(0, 1, 0)  # Plane is z=0
    d = Point3D(0.5, 0.5, -1)  # Point below
    assert orient3d(a, b, c, d) == 1


def test_orient3d_above():
    """Tests a simple case where d is above the plane abc."""
    a = Point3D(0, 0, 0)
    b = Point3D(1, 0, 0)
    c = Point3D(0, 1, 0)
    d = Point3D(0.5, 0.5, 1)  # Point above
    assert orient3d(a, b, c, d) == -1


def test_orient3d_coplanar():
    """Tests a simple case where d is on the plane abc."""
    a = Point3D(0, 0, 0)
    b = Point3D(1, 0, 0)
    c = Point3D(0, 1, 0)
    d = Point3D(0.5, 0.5, 0)  # Point on the plane
    assert orient3d(a, b, c, d) == 0


# --- Tests for incircle ---


def test_incircle_inside():
    """Tests a simple case where d is inside the circumcircle of abc."""
    a = Point2D(0, 1)
    b = Point2D(-1, 0)
    c = Point2D(1, 0)  # CCW order for a unit circle
    d = Point2D(0, 0)  # Point inside
    assert incircle(a, b, c, d) == 1


def test_incircle_outside():
    """Tests a simple case where d is outside the circumcircle of abc."""
    a = Point2D(0, 1)
    b = Point2D(-1, 0)
    c = Point2D(1, 0)
    d = Point2D(0, 2)  # Point outside
    assert incircle(a, b, c, d) == -1


def test_incircle_on_circle():
    """Tests a simple case where d is on the circumcircle of abc."""
    a = Point2D(0, 1)
    b = Point2D(-1, 0)
    c = Point2D(1, 0)
    d = Point2D(0, -1)  # Point on the circle
    assert incircle(a, b, c, d) == 0


# --- Tests for insphere ---


def test_insphere_placeholder():
    """Tests the insphere predicate - point inside the circumsphere returns -1."""
    a = Point3D(0, 0, 0)
    b = Point3D(1, 0, 0)
    c = Point3D(0, 1, 0)
    d = Point3D(0, 0, 1)
    e = Point3D(0.1, 0.1, 0.1)
    assert insphere(a, b, c, d, e) == -1
