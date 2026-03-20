
import pytest
import numpy as np
from compgeom.algo.hopper_optimizer import HopperOptimizer, hirsch_fitness, neighborly_fitness
from compgeom.kernel.polytope import HighDimPolytope

def test_hopper_optimizer_init():
    optimizer = HopperOptimizer(dim=3, num_initial_points=10)
    assert optimizer.dim == 3
    assert optimizer.polytope.dim == 3
    assert len(optimizer.polytope.points) == 10

def test_hopper_optimizer_run():
    optimizer = HopperOptimizer(dim=2, num_initial_points=5)
    
    def constant_fitness(poly):
        return 1.0
        
    best_poly, best_fit = optimizer.run(constant_fitness, iterations=10, num_agents=2)
    assert best_fit == 1.0
    assert isinstance(best_poly, HighDimPolytope)

def test_hirsch_fitness():
    # Square in 2D: n=4, d=2, diam=2. Fitness = 2 - (4 - 2) = 0
    points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
    poly = HighDimPolytope(points)
    assert hirsch_fitness(poly) == 0

def test_neighborly_fitness():
    points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
    poly = HighDimPolytope(points)
    fit = neighborly_fitness(poly, k=2)
    assert fit == pytest.approx(4 / 4) # 4 facets / 4 vertices
