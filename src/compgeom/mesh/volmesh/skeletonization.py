from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional
from compgeom.kernel import Point3D

class L1MedialSkeletonizer:
    """
    Implements the L1-Medial Skeleton algorithm.
    Huang et al., "L1-Medial Skeleton of Point Clouds", 2013.
    """
    def __init__(self, points: List[Point3D]):
        self.points = np.array([[p.x, p.y, p.z] for p in points])
        self.num_points = len(points)
        
    def skeletonize(self, sample_count: int = 100, iterations: int = 20, h: float = 0.1) -> List[Point3D]:
        """
        Extracts a set of skeleton points from the input point cloud.
        """
        # 1. Initialize skeleton points (samples) randomly from input
        indices = np.random.choice(self.num_points, sample_count, replace=False)
        X = self.points[indices].copy()
        
        # 2. Iterative L1-Medial Projection
        # x_i = [sum_j p_j * w_ij] / [sum_j w_ij]
        # where w_ij = exp(-|x_i - p_j|^2 / h^2) / |x_i - p_j|
        
        for _ in range(iterations):
            new_X = np.zeros_like(X)
            for i in range(sample_count):
                xi = X[i]
                dists = np.linalg.norm(self.points - xi, axis=1)
                
                # Avoid division by zero
                dists[dists < 1e-6] = 1e-6
                
                # Kernel weights
                theta = np.exp(-(dists**2) / (h**2))
                weights = theta / dists
                
                # Update position
                sum_w = np.sum(weights)
                if sum_w > 1e-12:
                    new_X[i] = np.sum(self.points * weights[:, np.newaxis], axis=0) / sum_w
                else:
                    new_X[i] = xi
            X = new_X
            
        return [Point3D(p[0], p[1], p[2]) for p in X]

    @staticmethod
    def extract_skeleton_edges(skeleton_points: List[Point3D], max_dist: float) -> List[Tuple[int, int]]:
        """
        Connects skeleton points into a graph based on proximity.
        """
        edges = []
        n = len(skeleton_points)
        for i in range(n):
            for j in range(i + 1, n):
                if skeleton_points[i].distance_to(skeleton_points[j]) < max_dist:
                    edges.append((i, j))
        return edges
