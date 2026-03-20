
import math
import pytest
from compgeom.kernel.point import Point2D, Point3D
from compgeom.kernel.transformation import Transformation

def test_identity():
    """Test the default identity transformation."""
    t = Transformation()
    p = Point3D(1, 2, 3)
    assert t.apply_to_point3d(p) == p

def test_translation():
    """Test the translation transformation."""
    t = Transformation.translation(10, -5, 2)
    p = Point3D(1, 2, 3)
    p_t = t.apply_to_point3d(p)
    assert p_t.x == pytest.approx(11)
    assert p_t.y == pytest.approx(-3)
    assert p_t.z == pytest.approx(5)
    
    p2d = Point2D(1, 2)
    p2d_t = t.apply_to_point2d(p2d)
    assert p2d_t.x == pytest.approx(11)
    assert p2d_t.y == pytest.approx(-3)

def test_scale():
    """Test the scale transformation."""
    t = Transformation.scale(2, 3, 4)
    p = Point3D(1, 2, 3)
    p_s = t.apply_to_point3d(p)
    assert p_s.x == pytest.approx(2)
    assert p_s.y == pytest.approx(6)
    assert p_s.z == pytest.approx(12)

def test_rotation_z_90_deg():
    """Test rotation around the Z-axis."""
    t = Transformation.rotation_z(math.pi / 2)
    p = Point3D(1, 0, 5)
    p_r = t.apply_to_point3d(p)
    assert p_r.x == pytest.approx(0)
    assert p_r.y == pytest.approx(1)
    assert p_r.z == pytest.approx(5)
    
    p2d = Point2D(1, 0)
    p2d_r = t.apply_to_point2d(p2d)
    assert p2d_r.x == pytest.approx(0)
    assert p2d_r.y == pytest.approx(1)

def test_rotation_x_90_deg():
    """Test rotation around the X-axis."""
    t = Transformation.rotation_x(math.pi / 2)
    p = Point3D(0, 1, 0)
    p_r = t.apply_to_point3d(p)
    assert p_r.x == pytest.approx(0)
    assert p_r.y == pytest.approx(0)
    assert p_r.z == pytest.approx(1)

def test_rotation_y_90_deg():
    """Test rotation around the Y-axis."""
    t = Transformation.rotation_y(math.pi / 2)
    p = Point3D(0, 0, 1)
    p_r = t.apply_to_point3d(p)
    assert p_r.x == pytest.approx(1)
    assert p_r.y == pytest.approx(0)
    assert p_r.z == pytest.approx(0)

def test_multiply():
    """Test matrix multiplication by composing transformations."""
    p = Point3D(1, 0, 0)
    
    # Create a translation and a rotation
    t = Transformation.translation(10, 0, 0)
    r = Transformation.rotation_z(math.pi / 2)
    
    # Apply one after the other
    p_manual = r.apply_to_point3d(t.apply_to_point3d(p))
    # p is at (1,0,0). After T, it's at (11,0,0). After R, it's at (0,11,0).
    assert p_manual.x == pytest.approx(0)
    assert p_manual.y == pytest.approx(11)
    
    # Apply the combined matrix
    m = r.multiply(t)
    p_combined = m.apply_to_point3d(p)
    
    assert p_combined == p_manual

def test_determinant():
    """Test determinant calculation."""
    # Identity
    t_id = Transformation()
    assert t_id.determinant() == pytest.approx(1.0)
    
    # Scale
    t_scale = Transformation.scale(2, 3, 4)
    assert t_scale.determinant() == pytest.approx(24.0)
    
    # Rotation
    t_rot = Transformation.rotation_x(1.23)
    assert t_rot.determinant() == pytest.approx(1.0)
    
    # Singular matrix
    t_singular = Transformation.scale(2, 3, 0)
    assert t_singular.determinant() == pytest.approx(0.0)

def test_inverse():
    """Test matrix inversion."""
    p = Point3D(1, 2, 3)
    
    # Create a composite transformation
    t = Transformation.translation(10, 5, -2)
    r = Transformation.rotation_z(0.5)
    s = Transformation.scale(2, 2, 2)
    m = t.multiply(r).multiply(s)
    
    # Get the inverse
    m_inv = m.inverse()
    assert m_inv is not None
    
    # Apply M then M_inv, should get original point back
    p_transformed = m.apply_to_point3d(p)
    p_restored = m_inv.apply_to_point3d(p_transformed)
    
    assert p_restored.x == pytest.approx(p.x)
    assert p_restored.y == pytest.approx(p.y)
    assert p_restored.z == pytest.approx(p.z)
    
    # Test inverse of a singular matrix
    t_singular = Transformation.scale(1, 1, 0)
    assert t_singular.inverse() is None
