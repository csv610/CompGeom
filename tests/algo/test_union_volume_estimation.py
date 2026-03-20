
import pytest
import numpy as np
from compgeom.kernel import Point3D, AABB3D
from compgeom.algo.union_volume_estimation import UnionVolumeEstimator

class MockSphere:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        # Correct order for AABB3D
        self.bbox = AABB3D(
            center.x - radius, center.y - radius, center.z - radius,
            center.x + radius, center.y + radius, center.z + radius
        )

    def contains(self, p):
        # p is a numpy array [x, y, z]
        return np.linalg.norm(p - np.array([self.center.x, self.center.y, self.center.z])) <= self.radius

def test_union_volume_estimator_simple():
    # Correct order for AABB3D
    bbox = AABB3D(0, 0, 0, 10, 10, 10)
    estimator = UnionVolumeEstimator(bbox, num_samples=1000)
    
    # A sphere at (5,5,5) with radius 2.
    # Volume should be roughly 4/3 * pi * 8 = 33.5
    s1 = MockSphere(Point3D(5, 5, 5), 2.0)
    vol1 = estimator.estimate([s1])
    assert 20 <= vol1 <= 50 # Heuristic check since it's Monte Carlo
    
    # Two identical spheres - union volume should be same
    vol2 = estimator.estimate([s1, s1])
    assert abs(vol2 - vol1) < 1e-9
    
    # Empty objects list
    assert estimator.estimate([]) == 0.0

def test_update_dynamic():
    bbox = AABB3D(0, 0, 0, 10, 10, 10)
    estimator = UnionVolumeEstimator(bbox, num_samples=100)
    s1 = MockSphere(Point3D(5, 5, 5), 1.0)
    assert estimator.update_dynamic([s1]) >= 0
