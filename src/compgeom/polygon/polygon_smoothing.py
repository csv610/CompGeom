"""Smoothing and curvature flow algorithms for polygons."""

from __future__ import annotations

import math
import cmath
from typing import List, Optional, Tuple

from ..kernel import Point2D
from ..kernel import distance


def fourier_smooth(
    polygon: List[Point2D], 
    n_harmonics: int = 10,
    resample_points: int = 128
) -> List[Point2D]:
    """
    Smooths a polygon using the Fourier method.
    
    1. Resamples the polygon into resample_points.
    2. Computes the Discrete Fourier Transform (DFT) of the vertices (as complex numbers).
    3. Retains only the first n_harmonics low-frequency components.
    4. Computes the inverse DFT to get the smoothed boundary.
    
    Args:
        polygon: List of points defining the polygon.
        n_harmonics: Number of low-frequency components to keep.
        resample_points: Number of points to resample the polygon into for DFT.
        
    Returns:
        A list of smoothed points.
    """
    if len(polygon) < 3:
        return polygon

    # 1. Resample
    resampled = PolygonalMeanCurvatureFlow.resample_polygon(polygon, resample_points)
    n = len(resampled)
    
    # 2. Represent as complex numbers
    z = [complex(p.x, p.y) for p in resampled]
    
    # 3. DFT
    # Z_m = sum_{k=0}^{n-1} z_k * exp(-i 2pi m k / n)
    # We only need the first n_harmonics components (0 to n_harmonics-1)
    # and the corresponding negative frequencies (n-n_harmonics+1 to n-1)
    # Actually, let's compute all and zero out the ones we don't want.
    
    # Simple DFT implementation (O(n^2))
    # For resample_points around 128-256, this is fine.
    Z = []
    for m in range(n):
        sum_val = complex(0, 0)
        for k in range(n):
            angle = -2 * math.pi * m * k / n
            sum_val += z[k] * cmath.exp(complex(0, angle))
        Z.append(sum_val)
        
    # 4. Low-pass filter
    # Keep components 0...n_harmonics and n-n_harmonics+1...n-1
    # DC component is m=0
    # Positive frequencies 1...n_harmonics
    # Negative frequencies n-n_harmonics...n-1
    for m in range(n):
        if n_harmonics < m < n - n_harmonics:
            Z[m] = complex(0, 0)
            
    # 5. Inverse DFT
    # z_k = (1/n) * sum_{m=0}^{n-1} Z_m * exp(i 2pi m k / n)
    smoothed_points = []
    for k in range(n):
        sum_val = complex(0, 0)
        for m in range(n):
            angle = 2 * math.pi * m * k / n
            sum_val += Z[m] * cmath.exp(complex(0, angle))
        
        val = sum_val / n
        smoothed_points.append(Point2D(val.real, val.imag))
        
    return smoothed_points


class PolygonalMeanCurvatureFlow:
    """Transforms a closed polygon to a circle using mean curvature flow."""

    @staticmethod
    def resample_polygon(polygon: List[Point2D], n_points: int) -> List[Point2D]:
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
            resampled.append(Point2D(
                p1.x + ratio * (p2.x - p1.x),
                p1.y + ratio * (p2.y - p1.y),
                i
            ))
            
        return resampled

    @staticmethod
    def smooth(
        polygon: List[Point2D], 
        iterations: int = 100, 
        time_step: float = 0.1,
        keep_perimeter: bool = True,
        fix_centroid: bool = True
    ) -> List[Point2D]:
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
            current = [Point2D(p.x - cx, p.y - cy, p.id) for p in current]

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
                
                next_poly.append(Point2D(
                    p_curr.x + time_step * laplacian_x,
                    p_curr.y + time_step * laplacian_y,
                    i
                ))
            
            # 2. Re-center to prevent drift
            if fix_centroid:
                cx, cy = get_centroid(next_poly)
                next_poly = [Point2D(p.x - cx, p.y - cy, p.id) for p in next_poly]

            # 3. Scale to preserve perimeter
            if keep_perimeter:
                current_p = calculate_perimeter(next_poly)
                if current_p > 0:
                    scale = original_perimeter / current_p
                    # Scaling is around the centroid (which is now 0,0)
                    next_poly = [
                        Point2D(p.x * scale, p.y * scale, p.id)
                        for p in next_poly
                    ]
            
            current = next_poly
            
        return current


__all__ = ["PolygonalMeanCurvatureFlow", "fourier_smooth"]
