"""Unit tests for Hopper-lite Polytope Discovery framework."""
import pytest
import numpy as np
from compgeom.kernel.polytope import HighDimPolytope
from compgeom.algo.hopper_optimizer import HopperOptimizer, hirsch_fitness

def test_polytope_diameter_cube():
    # 3D Unit Cube
    points = np.array([
        [0,0,0], [1,0,0], [0,1,0], [0,0,1],
        [1,1,0], [1,0,1], [0,1,1], [1,1,1]
    ])
    poly = HighDimPolytope(points)
    # Diameter of a cube is 3 (along the graph edges)
    # Path: (0,0,0) -> (1,0,0) -> (1,1,0) -> (1,1,1)
    assert poly.get_diameter() == 3

def test_polytope_diameter_simplex():
    # 3D Simplex (Tetrahedron)
    points = np.array([
        [0,0,0], [1,0,0], [0,1,0], [0,0,1]
    ])
    poly = HighDimPolytope(points)
    # Every vertex connected to every other vertex
    assert poly.get_diameter() == 1

def test_hopper_optimizer_short_run():
    # Run a tiny 3D optimization mission
    # Goal: just verify it evolves without crashing
    opt = HopperOptimizer(dim=3, num_initial_points=6)
    initial_facets = opt.polytope.num_facets
    
    # Target: maximize facet count
    def facet_fitness(p): return p.num_facets
    
    best_p, best_f = opt.run(facet_fitness, iterations=10, num_agents=2)
    assert best_p.num_facets >= initial_facets

def test_hirsch_fitness_basic():
    # Simple cube: n=6 (facets), d=3 (dim), delta=3 (diameter)
    # fitness = 3 - (6 - 3) = 0. Standard Hirsch bound is met.
    points = np.array([
        [0,0,0], [1,0,0], [0,1,0], [0,0,1],
        [1,1,0], [1,0,1], [0,1,1], [1,1,1]
    ])
    poly = HighDimPolytope(points)
    assert hirsch_fitness(poly) == 0
