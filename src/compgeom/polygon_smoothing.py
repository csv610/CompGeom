"""Smoothing and curvature flow algorithms for polygons."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from .geometry import Point
from .math_utils import distance


class PolygonalMeanCurvatureFlow:
    """Transforms a closed polygon to a circle using mean curvature flow."""

    @staticmethod
    def resample_polygon(polygon: List[Point], n_points: int) -> List[Point]:
        """Resamples a polygon uniformly into n_points at regular intervals."""
        if not polygon or n_points < 3:
            return polygon

        # 1. Calculate total perimeter and segment lengths
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

        # 2. Resample at regular intervals
        interval = perimeter / n_points
        resampled = []
        current_dist = 0.0
        orig_idx = 0
        dist_in_segment = 0.0

        for i in range(n_points):
            target_dist = i * interval
            
            # Find the segment containing the target distance
            while current_dist + segment_lengths[orig_idx] < target_dist:
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
        keep_perimeter: bool = True
    ) -> List[Point]:
        """
        Applies discrete mean curvature flow to smooth the polygon.
        
        Args:
            polygon: List of points defining the polygon.
            iterations: Number of smoothing steps.
            time_step: Step size for the flow (dt).
            keep_perimeter: If True, scales the polygon to maintain constant perimeter.
            
        Returns:
            The smoothed polygon.
        """
        if len(polygon) < 3:
            return polygon

        # Ensure uniform discretization before starting
        current = PolygonalMeanCurvatureFlow.resample_polygon(polygon, len(polygon))
        
        def calculate_perimeter(poly):
            p = 0.0
            n = len(poly)
            for i in range(n):
                p += distance(poly[i], poly[(i + 1) % n])
            return p

        original_perimeter = calculate_perimeter(current)

        for _ in range(iterations):
            n = len(current)
            next_poly = []
            
            for i in range(n):
                p_prev = current[(i - 1) % n]
                p_curr = current[i]
                p_next = current[(i + 1) % n]
                
                # Curvature vector approximated by Laplacian (central difference)
                # For uniform discretization, L = p_prev - 2*p_curr + p_next
                laplacian_x = p_prev.x - 2 * p_curr.x + p_next.x
                laplacian_y = p_prev.y - 2 * p_curr.y + p_next.y
                
                # Update position
                next_poly.append(Point(
                    p_curr.x + time_step * laplacian_x,
                    p_curr.y + time_step * laplacian_y,
                    i
                ))
            
            if keep_perimeter:
                current_p = calculate_perimeter(next_poly)
                if current_p > 0:
                    scale = original_perimeter / current_p
                    # Centroid-based scaling
                    sum_x = sum(p.x for p in next_poly) / n
                    sum_y = sum(p.y for p in next_poly) / n
                    next_poly = [
                        Point(
                            sum_x + (p.x - sum_x) * scale,
                            sum_y + (p.y - sum_y) * scale,
                            p.id
                        )
                        for p in next_poly
                    ]
            
            current = next_poly
            
        return current


__all__ = ["PolygonalMeanCurvatureFlow"]
