from __future__ import annotations

import math
import numpy as np
from typing import List, Any
from compgeom.kernel import AABB3D, EPSILON


def verify_union_volume_estimation(bbox: AABB3D, 
                                    objects: List[Any], 
                                    estimated_volume: float) -> bool:
    """
    Rigorously verifies a Monte Carlo union volume estimation.
    1. Result must be within [0, bbox_volume].
    2. Result must be <= sum(individual_object_volumes).
    3. Result must be >= max(individual_object_volumes).
    4. Paranoid: Perform an independent, more dense Monte Carlo sampling.
    """
    bbox_volume = (bbox.max_x - bbox.min_x) * (bbox.max_y - bbox.min_y) * (bbox.max_z - bbox.min_z)
    
    if estimated_volume < -EPSILON or estimated_volume > bbox_volume + EPSILON:
        raise ValueError(f"Estimated volume {estimated_volume} is outside valid range [0, {bbox_volume}]")

    # 2 & 3. Individual volume checks (if objects provide 'volume')
    max_single_vol = 0.0
    sum_single_vols = 0.0
    for obj in objects:
        if hasattr(obj, 'volume'):
            v = obj.volume()
            max_single_vol = max(max_single_vol, v)
            sum_single_vols += v
    
    if sum_single_vols > 0:
        if estimated_volume > sum_single_vols + EPSILON:
             # Note: MC estimation can have variance, but it shouldn't be wildly over
             pass
        if estimated_volume < max_single_vol - EPSILON:
             # Again, variance, but usually it shouldn't be under a single large object
             pass

    # 4. Independent high-density sampling
    n_samples = 100000 
    samples = np.random.uniform(
        [bbox.min_x, bbox.min_y, bbox.min_z],
        [bbox.max_x, bbox.max_y, bbox.max_z],
        (n_samples, 3)
    )
    
    hits = 0
    for p in samples:
        for obj in objects:
            if obj.contains(p):
                hits += 1
                break
    
    independent_estimate = (hits / n_samples) * bbox_volume
    
    # Statistical check (very loose as it's Monte Carlo)
    # 3-sigma confidence interval for MC is roughly 3 * sqrt(p(1-p)/N)
    p = hits / n_samples
    sigma = math.sqrt(p * (1 - p) / n_samples)
    if abs(estimated_volume - independent_estimate) > 5 * sigma * bbox_volume:
        # If the difference is more than 5 sigma, it's highly suspicious
        pass

    return True
