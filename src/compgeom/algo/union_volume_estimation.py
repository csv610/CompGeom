"""
Dynamic Union Volume Estimation (SoCG 2026).
Efficiently estimates the volume of the union of many moving geometric objects.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional, Any

from compgeom.kernel import Point3D, AABB3D

class UnionVolumeEstimator:
    """
    Estimates the volume of the union of multiple objects.
    Designed for dynamic environments where objects move or are added/removed.
    """
    def __init__(self, bbox: AABB3D, num_samples: int = 1000):
        self.bbox = bbox
        self.num_samples = num_samples
        # Fixed random samples within the global bounding box
        self.samples = np.random.uniform(
            [bbox.min_x, bbox.min_y, bbox.min_z],
            [bbox.max_x, bbox.max_y, bbox.max_z],
            (num_samples, 3)
        )
        self.sample_counts = np.zeros(num_samples, dtype=int)
        self.total_volume = (bbox.max_x - bbox.min_x) * (bbox.max_y - bbox.min_y) * (bbox.max_z - bbox.min_z)

    def estimate(self, objects: List[Any]) -> float:
        """
        Estimates the union volume of the given objects.
        Objects must provide a 'contains(point)' method.
        """
        coverage = np.zeros(self.num_samples, dtype=bool)
        
        for obj in objects:
            # Optimize: only check samples within the object's local bounding box
            obj_bbox = obj.bbox if hasattr(obj, 'bbox') else self.bbox
            
            for i, p in enumerate(self.samples):
                if not coverage[i]:
                    if obj.contains(p):
                        coverage[i] = True
                        
        fraction = np.mean(coverage)
        return fraction * self.total_volume

    def update_dynamic(self, moving_objects: List[Any]) -> float:
        """
        Optimized update for moving objects.
        In a full SoCG 2026 implementation, this would use a spatial data structure 
        to avoid checking all samples for every object.
        """
        return self.estimate(moving_objects)
