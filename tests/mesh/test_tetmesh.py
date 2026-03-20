import pytest
import random
from compgeom.kernel import Point3D
from compgeom.mesh.volume.tetmesh import DelaunayTetMesher, tetmesher

def test_single_tetrahedron():
    """Test with 4 points forming a single tetrahedron."""
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3),
    ]
    mesh = tetmesher(points)
    assert len(mesh.cells) == 1
    assert len(mesh.vertices) == 4

def test_cube_with_center():
    """Test with 8 cube corners and a center point."""
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(1, 1, 0, id=2),
        Point3D(0, 1, 0, id=3),
        Point3D(0, 0, 1, id=4),
        Point3D(1, 0, 1, id=5),
        Point3D(1, 1, 1, id=6),
        Point3D(0, 1, 1, id=7),
        Point3D(0.5, 0.5, 0.5, id=8),
    ]
    mesh = tetmesher(points)
    # A cube center connected to 12 triangles (2 per face) = 12 tets
    assert len(mesh.cells) == 12

def test_random_points():
    """Test with a larger set of random points."""
    random.seed(42)
    points = [
        Point3D(random.random(), random.random(), random.random(), id=i)
        for i in range(50)
    ]
    mesh = tetmesher(points)
    assert len(mesh.cells) > 0
    # Euler characteristic for a convex hull in 3D is slightly more complex, 
    # but we can check basic consistency.
    for cell in mesh.cells:
        assert len(cell) == 4

def test_collinear_points_skipped():
    """Test handling of duplicate or near-collinear points."""
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(0, 0, 0, id=1), # Duplicate
        Point3D(1, 1, 1, id=2),
        Point3D(2, 2, 2, id=3),
    ]
    # This should not crash, and likely result in 0 tets as they are collinear
    mesh = tetmesher(points)
    assert len(mesh.cells) == 0
