"""Tools for uniform sampling of polygon boundaries."""

from __future__ import annotations

from typing import Sequence, List, Tuple
from ..kernel import Point2D, distance, is_on_segment
from .polygon import Polygon
from .tolerance import is_zero


def get_perimeter_distances(vertices: Sequence[Point2D]) -> List[float]:
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
    fixed_nodes: Sequence[Point2D] | None = None
) -> List[Tuple[Point2D, float]]:
    """
    Uniformly samples the boundary of a closed polygon.
    """
    vertices = list(polygon.vertices)
    if not vertices:
        return []

    cum_dists = get_perimeter_distances(vertices)
    total_length = cum_dists[-1]
    
    if total_length == 0:
        return [(vertices[0], 0.0)]

    target_t = []
    
    if fixed_nodes:
        for node in fixed_nodes:
            t = get_parametric_coordinate(vertices, node)
            if t is not None:
                target_t.append(t)
    
    for i in range(num_samples):
        target_t.append(i / num_samples)
    
    target_t = sorted(list(set(target_t)))
    
    sampled_points = []
    for t in target_t:
        dist = t * total_length
        for i in range(len(cum_dists) - 1):
            if cum_dists[i] <= dist <= cum_dists[i+1]:
                p1 = vertices[i]
                p2 = vertices[(i + 1) % len(vertices)]
                
                seg_len = cum_dists[i+1] - cum_dists[i]
                if is_zero(seg_len, 1e-12):
                    sampled_points.append((p1, t))
                else:
                    ratio = (dist - cum_dists[i]) / seg_len
                    new_p = Point2D(
                        p1.x + ratio * (p2.x - p1.x),
                        p1.y + ratio * (p2.y - p1.y)
                    )
                    sampled_points.append((new_p, t))
                break
                
    return sampled_points


def get_parametric_coordinate(vertices: Sequence[Point2D], point: Point2D) -> float | None:
    """Find the parametric coordinate t in [0, 1) for a point on the polygon boundary."""
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
            return t % 1.0
            
    return None


__all__ = ["get_perimeter_distances", "sample_polygon_boundary", "get_parametric_coordinate"]
