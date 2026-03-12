"""Tools for uniform sampling of polygon boundaries."""

from __future__ import annotations

from typing import Sequence, List, Tuple
from ..kernel import Point, distance
from .polygon import Polygon

def get_perimeter_distances(vertices: Sequence[Point]) -> List[float]:
    """Calculate cumulative distance along the perimeter of the polygon."""
    n = len(vertices)
    if n == 0:
        return []
    
    dists = [0.0]
    total = 0.0
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        total += distance(p1, p2)
        dists.append(total)
    return dists

def sample_polygon_boundary(
    polygon: Polygon, 
    num_samples: int, 
    fixed_nodes: Sequence[Point] | None = None
) -> List[Tuple[Point, float]]:
    """
    Uniformly samples the boundary of a closed polygon.
    Returns a list of (Point, t) where t is the parametric coordinate in [0, 1).
    
    Args:
        polygon: The polygon to sample.
        num_samples: Number of points to sample.
        fixed_nodes: Optional list of points on the boundary that MUST be included.
    """
    vertices = list(polygon.vertices)
    if not vertices:
        return []

    # 1. Parameterize the boundary
    cum_dists = get_perimeter_distances(vertices)
    total_length = cum_dists[-1]
    
    if total_length == 0:
        return [(vertices[0], 0.0)]

    # 2. Identify target parametric coordinates
    # We want uniform sampling but must include fixed nodes
    target_t = []
    
    # Add fixed nodes first
    if fixed_nodes:
        for node in fixed_nodes:
            t = get_parametric_coordinate(vertices, node)
            if t is not None:
                target_t.append(t)
    
    # Add uniform samples
    for i in range(num_samples):
        target_t.append(i / num_samples)
    
    # Sort and remove duplicates
    target_t = sorted(list(set(target_t)))
    
    # 3. Interpolate to find points at target_t
    sampled_points = []
    for t in target_t:
        dist = t * total_length
        # Find which segment this distance falls into
        for i in range(len(cum_dists) - 1):
            if cum_dists[i] <= dist <= cum_dists[i+1]:
                p1 = vertices[i]
                p2 = vertices[(i + 1) % len(vertices)]
                
                seg_len = cum_dists[i+1] - cum_dists[i]
                if seg_len < 1e-12:
                    sampled_points.append((p1, t))
                else:
                    ratio = (dist - cum_dists[i]) / seg_len
                    new_p = Point(
                        p1.x + ratio * (p2.x - p1.x),
                        p1.y + ratio * (p2.y - p1.y)
                    )
                    sampled_points.append((new_p, t))
                break
                
    return sampled_points

def get_parametric_coordinate(vertices: Sequence[Point], point: Point) -> float | None:
    """Find the parametric coordinate t in [0, 1) for a point on the polygon boundary."""
    from ..kernel import is_on_segment
    
    cum_dists = get_perimeter_distances(vertices)
    total_length = cum_dists[-1]
    if total_length == 0:
        return 0.0
        
    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]
        
        if is_on_segment(point, p1, p2):
            dist_to_p1 = distance(p1, point)
            t = (cum_dists[i] + dist_to_p1) / total_length
            return t % 1.0 # Ensure it stays in [0, 1)
            
    return None
