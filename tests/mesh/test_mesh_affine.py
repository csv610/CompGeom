
import pytest
import math
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh import TriMesh
from compgeom.mesh.mesh_affine_transform import MeshAffineTransform

@pytest.fixture
def tri_3d():
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)]
    f = [(0,1,2)]
    return TriMesh(v, f)

@pytest.fixture
def tri_2d():
    v = [Point2D(0,0), Point2D(1,0), Point2D(0,1)]
    f = [(0,1,2)]
    return TriMesh(v, f)

def test_translate(tri_3d):
    MeshAffineTransform.translate(tri_3d, 10, 20, 30)
    assert tri_3d.vertices[0].x == 10
    assert tri_3d.vertices[0].y == 20
    assert tri_3d.vertices[0].z == 30

def test_scale(tri_2d):
    MeshAffineTransform.scale(tri_2d, 2, 3)
    assert tri_2d.vertices[1].x == 2
    assert tri_2d.vertices[2].y == 3

def test_rotate_z(tri_2d):
    # Rotate (1,0) by 90 deg around Z -> (0,1)
    MeshAffineTransform.rotate(tri_2d, 90, axis='z')
    assert tri_2d.vertices[1].x == pytest.approx(0)
    assert tri_2d.vertices[1].y == pytest.approx(1)

def test_rotate_x(tri_3d):
    # Rotate (0,1,0) by 90 deg around X -> (0,0,1)
    MeshAffineTransform.rotate(tri_3d, 90, axis='x')
    assert tri_3d.vertices[2].y == pytest.approx(0)
    assert tri_3d.vertices[2].z == pytest.approx(1)

def test_rotate_y(tri_3d):
    # Rotate (1,0,0) by 90 deg around Y -> (0,0,-1)
    MeshAffineTransform.rotate(tri_3d, 90, axis='y')
    assert tri_3d.vertices[1].x == pytest.approx(0)
    assert tri_3d.vertices[1].z == pytest.approx(-1)

def test_normalize(tri_3d):
    # tri_3d is (0,0,0), (1,0,0), (0,1,0)
    # Bbox: (0,0,0) to (1,1,0)
    # max_dim = 1. Center = (0.5, 0.5, 0)
    # After normalization: center at (0,0,0), fits in [-1, 1]
    MeshAffineTransform.normalize(tri_3d)
    
    pts = tri_3d.vertices
    # Center should be origin
    cx = sum(p.x for p in pts) / 3
    cy = sum(p.y for p in pts) / 3
    # Wait, normalize centers based on bbox, not centroid.
    # Original bbox: [0,1]x[0,1]x[0,0]
    # Centered bbox: [-0.5, 0.5]x[-0.5, 0.5]x[0,0]
    # Scaled by 2.0 / max_dim (1.0) -> [-1, 1]x[-1, 1]x[0,0]
    
    assert min(p.x for p in pts) == pytest.approx(-1.0)
    assert max(p.x for p in pts) == pytest.approx(1.0)
    assert min(p.y for p in pts) == pytest.approx(-1.0)
    assert max(p.y for p in pts) == pytest.approx(1.0)
