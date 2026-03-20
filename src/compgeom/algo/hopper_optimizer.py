"""Multi-agent optimizer for discovering extremal polytopes."""
from __future__ import annotations
import numpy as np
from typing import List, Tuple, Callable, Optional
import copy

from compgeom.kernel.polytope import HighDimPolytope

class HopperOptimizer:
    """
    Search engine for extremal polytopes.
    Inspired by the multi-agent approach in DeepMind's Hopper.
    """
    def __init__(self, dim: int, num_initial_points: int):
        self.dim = dim
        # Initialize with random points in [0, 1]^d
        pts = np.random.rand(num_initial_points, dim)
        self.polytope = HighDimPolytope(pts)
        self.best_polytope = copy.deepcopy(self.polytope)
        self.best_fitness = -float('inf')

    def run(self, fitness_func: Callable[[HighDimPolytope], float], 
            iterations: int = 100, 
            num_agents: int = 5):
        """
        Runs the multi-agent search loop.
        """
        for i in range(iterations):
            # Simulation of multiple agents exploring mutations
            for _ in range(num_agents):
                candidate = copy.deepcopy(self.polytope)
                
                # Randomized actions
                action = np.random.choice(['perturb', 'add', 'prune'])
                if action == 'perturb':
                    candidate.mutate_perturb(sigma=0.05)
                elif action == 'add':
                    # Add a point near the center of a random facet
                    if candidate._hull is not None:
                        f_idx = np.random.choice(len(candidate._hull.simplices))
                        facet = candidate._hull.simplices[f_idx]
                        center = np.mean(candidate.points[facet], axis=0)
                        # Offset slightly along normal
                        normal = candidate._hull.equations[f_idx, :-1]
                        new_p = center + 0.1 * normal
                        candidate.add_point(new_p)
                elif action == 'prune':
                    candidate.prune_redundant()
                
                # Evaluate
                fit = fitness_func(candidate)
                if fit > self.best_fitness:
                    self.best_fitness = fit
                    self.best_polytope = copy.deepcopy(candidate)
                    self.polytope = copy.deepcopy(candidate) # Greedily follow improvement
                elif np.random.rand() < 0.1:
                    # Occasional acceptance of worse states (Simulated Annealing style)
                    self.polytope = copy.deepcopy(candidate)

        return self.best_polytope, self.best_fitness

def hirsch_fitness(poly: HighDimPolytope) -> float:
    """
    Objective: diameter(P) - (num_facets - dim)
    If positive, we have a counterexample to Hirsch Conjecture.
    Note: Standard Hirsch is facets, but many variants use vertices.
    The 2025 paper focuses on diameter vs facets.
    """
    n = poly.num_facets
    d = poly.dim
    delta = poly.get_diameter()
    # f(P) = diameter - (n - d)
    return delta - (n - d)

def neighborly_fitness(poly: HighDimPolytope, k: int) -> float:
    """
    Objective: fraction of k-vertex sets that are faces.
    Maximizing this finds k-neighborly polytopes.
    """
    # For performance in high-D, we use a heuristic proxy: 
    # ratio of facet count to vertex count.
    return poly.num_facets / (poly.num_vertices + 1e-9)
