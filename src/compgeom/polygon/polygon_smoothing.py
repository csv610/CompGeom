"""Smoothing and curvature flow algorithms for polygons."""

from __future__ import annotations

import math
import cmath
from typing import List, Sequence

from ..kernel import Point2D, distance
from .polygon import Polygon
from .tolerance import EPSILON


def resample_polygon(polygon: Polygon | Sequence[Point2D], n_points: int) -> list[Point2D]:
    """Resamples a polygon uniformly into n_points at regular intervals."""
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    vertices = poly_obj.vertices
    if not vertices or n_points < 3:
        return list(vertices)

    perimeter = 0.0
    n_orig = len(vertices)
    segment_lengths = []
    for i in range(n_orig):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n_orig]
        d = distance(p1, p2)
        segment_lengths.append(d)
        perimeter += d

    if perimeter <= 0:
        return list(vertices)

    interval = perimeter / n_points
    resampled = []
    current_dist = 0.0
    orig_idx = 0

    for i in range(n_points):
        target_dist = i * interval
        
        while current_dist + segment_lengths[orig_idx] < target_dist - EPSILON:
            current_dist += segment_lengths[orig_idx]
            orig_idx = (orig_idx + 1) % n_orig
        
        dist_in_segment = target_dist - current_dist
        p1 = vertices[orig_idx]
        p2 = vertices[(orig_idx + 1) % n_orig]
        
        ratio = dist_in_segment / segment_lengths[orig_idx] if segment_lengths[orig_idx] > 0 else 0
        resampled.append(Point2D(
            p1.x + ratio * (p2.x - p1.x),
            p1.y + ratio * (p2.y - p1.y),
            i
        ))
        
    return resampled


def fourier_smooth_polygon(
    polygon: Polygon | Sequence[Point2D], 
    n_harmonics: int = 10,
    resample_points: int = 128
) -> list[Point2D]:
    """Smooths a polygon using the Fourier method."""
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    vertices = poly_obj.vertices
    if len(vertices) < 3:
        return list(vertices)

    resampled = resample_polygon(poly_obj, resample_points)
    n = len(resampled)
    z = [complex(p.x, p.y) for p in resampled]
    
    Z = []
    for m in range(n):
        sum_val = complex(0, 0)
        for k in range(n):
            angle = -2 * math.pi * m * k / n
            sum_val += z[k] * cmath.exp(complex(0, angle))
        Z.append(sum_val)
        
    for m in range(n):
        if n_harmonics < m < n - n_harmonics:
            Z[m] = complex(0, 0)
            
    smoothed_points = []
    for k in range(n):
        sum_val = complex(0, 0)
        for m in range(n):
            angle = 2 * math.pi * m * k / n
            sum_val += Z[m] * cmath.exp(complex(0, angle))
        
        val = sum_val / n
        smoothed_points.append(Point2D(val.real, val.imag))
        
    return smoothed_points


def mean_curvature_flow_polygon(
    polygon: Polygon | Sequence[Point2D], 
    iterations: int = 100, 
    time_step: float = 0.1,
    keep_perimeter: bool = True,
    fix_centroid: bool = True
) -> list[Point2D]:
    """Applies discrete mean curvature flow to smooth the polygon."""
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    vertices = poly_obj.vertices
    if len(vertices) < 3:
        return list(vertices)

    n = len(vertices)
    current = list(vertices)
    
    def calculate_perimeter(poly):
        p = 0.0
        for i in range(len(poly)):
            p += distance(poly[i], poly[(i + 1) % len(poly)])
        return p

    # Initial centering
    if fix_centroid:
        props = Polygon(current).properties()
        cx, cy = props.centroid.x, props.centroid.y
        current = [Point2D(p.x - cx, p.y - cy, getattr(p, "id", None)) for p in current]

    original_perimeter = calculate_perimeter(current)

    for _ in range(iterations):
        next_poly = []
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
        
        if fix_centroid:
            props = Polygon(next_poly).properties()
            cx, cy = props.centroid.x, props.centroid.y
            next_poly = [Point2D(p.x - cx, p.y - cy, getattr(p, "id", None)) for p in next_poly]

        if keep_perimeter:
            current_p = calculate_perimeter(next_poly)
            if current_p > 0:
                scale = original_perimeter / current_p
                next_poly = [
                    Point2D(p.x * scale, p.y * scale, getattr(p, "id", None))
                    for p in next_poly
                ]
        
        current = next_poly
        
    return current


__all__ = ["resample_polygon", "fourier_smooth_polygon", "mean_curvature_flow_polygon"]
