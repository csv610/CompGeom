from __future__ import annotations

from typing import List
from compgeom.kernel import Point2D, EPSILON
from compgeom.polygon.convex_hull import ConvexHull
from compgeom.verifiers.polygon.polygon_verifiers import verify_convex_hull


def verify_convex_hull_peeling(points: List[Point2D], 
                               layers: List[List[Point2D]]) -> bool:
    """
    Rigorously verifies convex hull peeling (onion peeling).
    1. The union of points in all layers must be equal to the unique input points.
    2. Each layer must be a valid convex hull of the points remaining at that step.
    3. Layers must be nested: Layer i must contain all points in Layer i+1, i+2, ...
    """
    if not points:
        return not layers

    unique_input = set(points)
    all_layer_points = []
    for layer in layers:
        all_layer_points.extend(layer)
    
    # 1. Union check
    if set(all_layer_points) != unique_input:
        raise ValueError("Union of all layers does not match the set of unique input points")
    
    if len(all_layer_points) != len(set(all_layer_points)):
        # Check if points are duplicated across layers
        seen = set()
        for layer in layers:
            for p in layer:
                if p in seen:
                    raise ValueError(f"Point {p} appears in multiple layers")
                seen.add(p)

    # 2 & 3. Sequential hull and nesting check
    current_remaining = list(unique_input)
    for i, layer in enumerate(layers):
        # The i-th layer MUST be the convex hull of current_remaining
        # verify_convex_hull is already paranoid
        try:
            verify_convex_hull(current_remaining, layer)
        except ValueError as e:
            raise ValueError(f"Layer {i} is not a valid convex hull of remaining points: {e}")
            
        # Update remaining
        layer_set = set(layer)
        current_remaining = [p for p in current_remaining if p not in layer_set]
        
        # Nesting is implicitly checked because verify_convex_hull ensures 'layer' 
        # contains all 'current_remaining' points.

    return True
