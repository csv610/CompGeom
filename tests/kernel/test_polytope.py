
import numpy as np
import pytest

from compgeom.kernel.polytope import HighDimPolytope

def test_polytope_2d_square():
    """Tests basic properties of a 2D square polytope."""
    points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
    poly = HighDimPolytope(points)
    
    assert poly.dim == 2
    assert poly.num_vertices == 4
    assert poly.num_facets == 4 # In 2D, facets are edges
    assert poly.get_diameter() == 2

def test_polytope_3d_cube():
    """Tests basic properties of a 3D cube polytope."""
    points = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
    ])
    poly = HighDimPolytope(points)
    
    assert poly.dim == 3
    assert poly.num_vertices == 8
    assert poly.num_facets == 6
    assert poly.get_diameter() == 3

def test_polytope_insufficient_points():
    """Tests initialization with not enough points to form a hull."""
    points = np.array([[0, 0], [1, 0]]) # 2 points in 2D, need 3
    poly = HighDimPolytope(points)
    assert poly.dim == 2
    assert poly._hull is None
    assert poly.num_vertices == 0
    assert poly.num_facets == 0
    assert poly.get_diameter() == 0

def test_polytope_collinear_points():
    """Tests initialization with collinear points which should fail hull creation."""
    points = np.array([[0, 0], [1, 0], [2, 0], [3, 0]])
    poly = HighDimPolytope(points)
    # ConvexHull fails for degenerate, non-dimensional input.
    assert poly.dim == 2
    assert poly._hull is None
    assert poly.num_vertices == 0
    assert poly.num_facets == 0

def test_add_point():
    """Tests the add_point method."""
    points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
    poly = HighDimPolytope(points)
    assert poly.num_vertices == 4
    
    # Add a point inside the hull, vertices should not change
    poly.add_point(np.array([0.5, 0.5]))
    assert poly.num_vertices == 4
    
    # Add a point outside the hull. For this specific geometry, the number of
    # vertices in the new hull is 4, as the old vertex (1,1) is replaced.
    poly.add_point(np.array([2, 2]))
    assert poly.num_vertices == 4

def test_prune_redundant():
    """Tests the prune_redundant method."""
    points = np.array([
        [0, 0], [1, 0], [1, 1], [0, 1], # The hull
        [0.5, 0.5], [0.2, 0.3]        # Redundant points
    ])
    poly = HighDimPolytope(points)
    assert len(poly.points) == 6
    assert poly.num_vertices == 4
    
    poly.prune_redundant()
    assert len(poly.points) == 4
    # Check that the remaining points are the hull vertices
    hull_points = points[[0, 1, 3, 2]] # Note: ConvexHull may reorder vertices
    assert set(map(tuple, poly.points)) == set(map(tuple, hull_points))


def test_mutate_perturb():
    """Tests the mutate_perturb method."""
    points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
    poly = HighDimPolytope(points.copy())
    
    original_points = poly.points.copy()
    poly.mutate_perturb(sigma=0.1)
    
    assert not np.allclose(original_points, poly.points)

def test_num_facets_with_coplanar():
    """Tests that num_facets correctly merges coplanar facets."""
    points = np.array([
        [0, 0, 0], [1, 0, 0], [0.5, 1, 0], # Bottom triangle
        [0, 0, 1], [1, 0, 1], [0.5, 1, 1]  # Top triangle
    ])
    poly = HighDimPolytope(points)
    assert poly.dim == 3
    assert poly.num_vertices == 6
    # Should be 5 facets: 3 sides + 1 top + 1 bottom
    assert poly.num_facets == 5
