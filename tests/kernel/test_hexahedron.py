
import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.kernel import hexahedron as hex_module
from compgeom.kernel.hexahedron import Hexahedron

@pytest.fixture
def unit_cube_vertices():
    """Returns the 8 vertices of a unit cube."""
    return (
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
        Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)
    )

@pytest.fixture
def unit_cube(unit_cube_vertices):
    """Returns a Hexahedron instance for a unit cube."""
    return Hexahedron(*unit_cube_vertices)

def test_class_properties(unit_cube, unit_cube_vertices):
    """Test the basic properties of the Hexahedron class."""
    assert unit_cube.vertices == unit_cube_vertices
    assert unit_cube.centroid() == Point3D(0.5, 0.5, 0.5)
    assert unit_cube.volume() == pytest.approx(1.0)
    assert unit_cube.is_convex() is True

def test_centroid(unit_cube_vertices):
    """Test the standalone centroid function."""
    assert hex_module.centroid(*unit_cube_vertices) == Point3D(0.5, 0.5, 0.5)

def test_volume(unit_cube_vertices):
    """Test the standalone volume function."""
    assert hex_module.volume(*unit_cube_vertices) == pytest.approx(1.0)

def test_is_convex(unit_cube_vertices):
    """Test the standalone is_convex function."""
    assert hex_module.is_convex(*unit_cube_vertices) is True
    
    # Create a non-convex hex by moving a vertex across a face plane
    v = list(unit_cube_vertices)
    v[6] = Point3D(1, 1, -0.1) # Move v7 across the bottom face
    assert hex_module.is_convex(*v) is False

def test_contains_point(unit_cube_vertices):
    """Test the standalone contains_point function."""
    center = Point3D(0.5, 0.5, 0.5)
    outside = Point3D(2, 2, 2)
    on_face = Point3D(0.5, 0.5, 0)
    
    assert hex_module.contains_point(center, *unit_cube_vertices) is True
    assert hex_module.contains_point(outside, *unit_cube_vertices) is False
    assert hex_module.contains_point(on_face, *unit_cube_vertices) is True

def test_faces(unit_cube_vertices):
    """Test the faces function."""
    faces = hex_module.faces(*unit_cube_vertices)
    assert len(faces) == 6
    # Check bottom face (v1,v4,v3,v2)
    assert faces[0] == (unit_cube_vertices[0], unit_cube_vertices[3], unit_cube_vertices[2], unit_cube_vertices[1])

def test_edges(unit_cube_vertices):
    """Test the edges function."""
    edges = hex_module.edges(*unit_cube_vertices)
    assert len(edges) == 12
    # Check one bottom edge and one vertical edge
    assert edges[0] == (unit_cube_vertices[0], unit_cube_vertices[1])
    assert edges[8] == (unit_cube_vertices[0], unit_cube_vertices[4])

def test_min_sphere(unit_cube_vertices):
    """Test the min_sphere function for a unit cube."""
    s = hex_module.min_sphere(*unit_cube_vertices)
    assert s.center == Point3D(0.5, 0.5, 0.5)
    assert s.radius == pytest.approx(np.sqrt(0.75))

def test_barycentric_coords(unit_cube_vertices):
    """Test the barycentric_coords function."""
    # Test the center point
    p_center = Point3D(0.5, 0.5, 0.5)
    u, v, w = hex_module.barycentric_coords(p_center, *unit_cube_vertices)
    assert u == pytest.approx(0.5)
    assert v == pytest.approx(0.5)
    assert w == pytest.approx(0.5)
    
    # Test a vertex
    v1 = unit_cube_vertices[0]
    u, v, w = hex_module.barycentric_coords(v1, *unit_cube_vertices)
    assert u == pytest.approx(0.0)
    assert v == pytest.approx(0.0)
    assert w == pytest.approx(0.0)
