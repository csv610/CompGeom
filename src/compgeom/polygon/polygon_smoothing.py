"""Smoothing and curvature flow algorithms for polygons and meshes."""

from __future__ import annotations

import math
import cmath
import random
from typing import List, Sequence, Union, TypeVar

from compgeom.kernel import Point2D, Point3D, distance
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.tolerance import EPSILON
from compgeom.mesh.mesh_base import Mesh, MeshNode

T = TypeVar("T", Polygon, Mesh, Sequence[Point2D])


def resample_polygon(polygon: Union[Polygon, Mesh, Sequence[Point2D]], n_points: int) -> list[Point2D]:
    """Resamples a polygon uniformly into n_points at regular intervals."""
    if isinstance(polygon, Mesh):
        if polygon.faces:
            from compgeom.mesh.mesh_topology import MeshTopology
            loops = MeshTopology(polygon).boundary_loops()
            if loops:
                # Use the largest loop
                loop_idx = max(range(len(loops)), key=lambda i: len(loops[i]))
                vertices = [polygon.vertices[i] for i in loops[loop_idx]]
            else:
                vertices = polygon.vertices
        else:
            vertices = polygon.vertices
    elif isinstance(polygon, Polygon):
        vertices = polygon.vertices
    else:
        vertices = list(polygon)

    if not vertices or n_points < 3:
        return [Point2D(p.x, p.y) for p in vertices]

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
        return [Point2D(p.x, p.y) for p in vertices]

    interval = perimeter / n_points
    resampled = []
    current_dist = 0.0
    orig_idx = 0

    for i in range(n_points):
        target_dist = i * interval
        
        while current_dist + segment_lengths[orig_idx] < target_dist - EPSILON:
            current_dist += segment_lengths[orig_idx]
            orig_idx = (orig_idx + 1) % n_orig
            if orig_idx == 0 and i > 0: # Wrapped around
                break
        
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
    polygon: Union[Polygon, Mesh, Sequence[Point2D]], 
    n_harmonics: int = 10,
    resample_points: int = 128
) -> list[Point2D]:
    """Smooths a polygon using the Fourier method."""
    resampled = resample_polygon(polygon, resample_points)
    n = len(resampled)
    if n < 3:
        return resampled

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
    polygon: T, 
    iterations: int = 100, 
    time_step: float | None = None,
    keep_perimeter: bool = True,
    fix_centroid: bool = True,
    n_points: int | None = None
) -> T:
    """Applies discrete mean curvature flow to smooth the polygon or mesh.
    
    If n_points and time_step are not provided, they are determined adaptively.
    Early termination if the shape becomes circular.
    Extracts boundary edges automatically if input is a mesh with faces.
    """
    orig_type = type(polygon)
    is_mesh = isinstance(polygon, Mesh)

    if is_mesh and polygon.faces:
        from compgeom.mesh.mesh_topology import MeshTopology
        loops = MeshTopology(polygon).boundary_loops()
        if loops:
            # Use the largest loop
            loop_idx = max(range(len(loops)), key=lambda i: len(loops[i]))
            # Convert mesh to a simple sequence of vertices from the boundary loop
            polygon_data = [polygon.vertices[i] for i in loops[loop_idx]]
        else:
            polygon_data = polygon.vertices
    elif isinstance(polygon, Mesh):
        polygon_data = polygon.vertices
    elif isinstance(polygon, Polygon):
        polygon_data = polygon.vertices
    else:
        polygon_data = list(polygon)

    if n_points is None:
        n_points = n_points or len(polygon_data)
    
    current_n_points = n_points
    current = resample_polygon(polygon_data, current_n_points)

    if time_step is None:
        dt = 0.05
    else:
        dt = time_step

    def calculate_perimeter(poly):
        p = 0.0
        for i in range(len(poly)):
            p += distance(poly[i], poly[(i + 1) % len(poly)])
        return p
    
    def calculate_area_2d(poly):
        a = 0.0
        for i in range(len(poly)):
            p1 = poly[i]
            p2 = poly[(i + 1) % len(poly)]
            a += (p1.x * p2.y) - (p2.x * p1.y)
        return abs(a) / 2.0

    original_perimeter = calculate_perimeter(current)

    for iter_idx in range(iterations):
        # Check for circularity
        area = calculate_area_2d(current)
        peri = calculate_perimeter(current)
        if peri > 0:
            circularity = (4 * math.pi * area) / (peri * peri)
            if circularity > 0.99: # Practically a circle
                break

        while True:
            n = len(current)
            if n < 3:
                break
            
            next_poly = []
            max_move = 0.0
            
            # Calculate average edge length to use as threshold
            total_edge_len = 0.0
            for i in range(n):
                total_edge_len += distance(current[i], current[(i+1)%n])
            avg_edge_len = total_edge_len / n if n > 0 else 1.0
            
            threshold = 0.2 * avg_edge_len # Move at most 20% of an edge
            
            for i in range(n):
                p_prev = current[(i - 1) % n]
                p_curr = current[i]
                p_next = current[(i + 1) % n]
                
                laplacian_x = p_prev.x - 2 * p_curr.x + p_next.x
                laplacian_y = p_prev.y - 2 * p_curr.y + p_next.y
                
                new_x = p_curr.x + dt * laplacian_x
                new_y = p_curr.y + dt * laplacian_y
                
                move = math.sqrt((new_x - p_curr.x)**2 + (new_y - p_curr.y)**2)
                max_move = max(max_move, move)
                
                if isinstance(p_curr, Point3D):
                    laplacian_z = p_prev.z - 2 * p_curr.z + p_next.z
                    new_z = p_curr.z + dt * laplacian_z
                    next_poly.append(Point3D(new_x, new_y, new_z, i))
                else:
                    next_poly.append(Point2D(new_x, new_y, i))
            
            if max_move > threshold and dt > 1e-6:
                dt /= 2.0
                current_n_points = int(current_n_points * 1.1)
                current = resample_polygon(current, current_n_points)
                # Retry step with smaller dt and more points
                continue
            else:
                current = next_poly
                break
        
        # Centering and perimeter maintenance
        n = len(current)
        if n < 3:
            break
            
        if fix_centroid:
            cx = sum(p.x for p in current) / n
            cy = sum(p.y for p in current) / n
            if isinstance(current[0], Point3D):
                cz = sum(p.z for p in current) / n
                current = [Point3D(p.x - cx, p.y - cy, p.z - cz, getattr(p, "id", None)) for p in current]
            else:
                current = [Point2D(p.x - cx, p.y - cy, getattr(p, "id", None)) for p in current]

        if keep_perimeter:
            current_p = calculate_perimeter(current)
            if current_p > 0:
                scale = original_perimeter / current_p
                if isinstance(current[0], Point3D):
                    current = [
                        Point3D(p.x * scale, p.y * scale, p.z * scale, getattr(p, "id", None))
                        for p in current
                    ]
                else:
                    current = [
                        Point2D(p.x * scale, p.y * scale, getattr(p, "id", None))
                        for p in current
                    ]
    
    if is_mesh:
        from compgeom.mesh.surface.polygon.polygon import PolygonMesh
        return PolygonMesh(current, [tuple(range(len(current)))])
    elif issubclass(orig_type, Polygon):
        return Polygon(current)
    else:
        return current


__all__ = ["resample_polygon", "fourier_smooth_polygon", "mean_curvature_flow_polygon"]
