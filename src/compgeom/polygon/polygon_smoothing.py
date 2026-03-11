"""Smoothing and curvature flow algorithms for polygons."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from ..kernel import Point
from ..kernel import distance


class PolygonalMeanCurvatureFlow:
    """Transforms a closed polygon to a circle using mean curvature flow."""

    @staticmethod
    def resample_polygon(polygon: List[Point], n_points: int) -> List[Point]:
        """Resamples a polygon uniformly into n_points at regular intervals."""
        if not polygon or n_points < 3:
            return polygon

        perimeter = 0.0
        n_orig = len(polygon)
        segment_lengths = []
        for i in range(n_orig):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n_orig]
            d = distance(p1, p2)
            segment_lengths.append(d)
            perimeter += d

        if perimeter <= 0:
            return polygon

        interval = perimeter / n_points
        resampled = []
        current_dist = 0.0
        orig_idx = 0

        for i in range(n_points):
            target_dist = i * interval
            
            while current_dist + segment_lengths[orig_idx] < target_dist - 1e-9:
                current_dist += segment_lengths[orig_idx]
                orig_idx = (orig_idx + 1) % n_orig
            
            dist_in_segment = target_dist - current_dist
            p1 = polygon[orig_idx]
            p2 = polygon[(orig_idx + 1) % n_orig]
            
            ratio = dist_in_segment / segment_lengths[orig_idx] if segment_lengths[orig_idx] > 0 else 0
            resampled.append(Point(
                p1.x + ratio * (p2.x - p1.x),
                p1.y + ratio * (p2.y - p1.y),
                i
            ))
            
        return resampled

    @staticmethod
    def smooth(
        polygon: List[Point], 
        iterations: int = 100, 
        time_step: float = 0.1,
        keep_perimeter: bool = True,
        fix_centroid: bool = True
    ) -> List[Point]:
        """
        Applies discrete mean curvature flow to smooth the polygon.
        
        Args:
            polygon: List of points defining the polygon.
            iterations: Number of smoothing steps.
            time_step: Step size for the flow (dt).
            keep_perimeter: If True, scales the polygon to maintain constant perimeter.
            fix_centroid: If True, the centroid is kept at (0,0).
        """
        if len(polygon) < 3:
            return polygon

        n = len(polygon)
        current = list(polygon)
        
        def calculate_perimeter(poly):
            p = 0.0
            for i in range(len(poly)):
                p += distance(poly[i], poly[(i + 1) % len(poly)])
            return p

        def get_centroid(poly):
            cx = sum(p.x for p in poly) / len(poly)
            cy = sum(p.y for p in poly) / len(poly)
            return cx, cy

        # Initial centering
        if fix_centroid:
            cx, cy = get_centroid(current)
            current = [Point(p.x - cx, p.y - cy, p.id) for p in current]

        original_perimeter = calculate_perimeter(current)

        for _ in range(iterations):
            next_poly = []
            
            # 1. Laplacian Step
            for i in range(n):
                p_prev = current[(i - 1) % n]
                p_curr = current[i]
                p_next = current[(i + 1) % n]
                
                laplacian_x = p_prev.x - 2 * p_curr.x + p_next.x
                laplacian_y = p_prev.y - 2 * p_curr.y + p_next.y
                
                next_poly.append(Point(
                    p_curr.x + time_step * laplacian_x,
                    p_curr.y + time_step * laplacian_y,
                    i
                ))
            
            # 2. Re-center to prevent drift
            if fix_centroid:
                cx, cy = get_centroid(next_poly)
                next_poly = [Point(p.x - cx, p.y - cy, p.id) for p in next_poly]

            # 3. Scale to preserve perimeter
            if keep_perimeter:
                current_p = calculate_perimeter(next_poly)
                if current_p > 0:
                    scale = original_perimeter / current_p
                    # Scaling is around the centroid (which is now 0,0)
                    next_poly = [
                        Point(p.x * scale, p.y * scale, p.id)
                        for p in next_poly
                    ]
            
            current = next_poly
            
        return current


__all__ = ["PolygonalMeanCurvatureFlow"]
