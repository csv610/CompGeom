"""Solvers for Eikonal equations and distance maps."""

from __future__ import annotations

import math
from typing import List, Tuple, Union

from compgeom.kernel import Point2D, dist_point_to_segment
from compgeom.polygon.polygon_metrics import get_polygon_properties


def solve_distance_map(
    polygon: List[Point2D], 
    resolution: int = 100, 
    padding: float = 0.1
) -> Tuple[List[List[float]], Tuple[float, float, float, float]]:
    """
    Solves the Eikonal equation |grad u| = 1 using the Fast Sweeping Method.
    
    Args:
        polygon: List of points defining the boundary.
        resolution: Number of grid cells along the longest dimension.
        padding: Extra space around the bounding box.
        
    Returns:
        A tuple (grid, extent) where grid is a 2D list of distances and 
        extent is (min_x, max_x, min_y, max_y).
    """
    if not polygon:
        return [[]], (0, 0, 0, 0)

    # 1. Setup grid
    min_x = min(p.x for p in polygon)
    max_x = max(p.x for p in polygon)
    min_y = min(p.y for p in polygon)
    max_y = max(p.y for p in polygon)
    
    dx_poly = max_x - min_x
    dy_poly = max_y - min_y
    
    # Apply padding
    min_x -= dx_poly * padding
    max_x += dx_poly * padding
    min_y -= dy_poly * padding
    max_y += dy_poly * padding
    
    width = max_x - min_x
    height = max_y - min_y
    
    if width > height:
        nx = resolution
        ny = max(3, int(resolution * (height / width)))
    else:
        ny = resolution
        nx = max(3, int(resolution * (width / height)))
        
    h = width / (nx - 1) if nx > 1 else 1.0
    
    # Initialize grid with infinity
    grid = [[float('inf')] * ny for _ in range(nx)]
    
    # 2. Boundary conditions: u=0 on the polygon edges
    for i in range(nx):
        for j in range(ny):
            px = min_x + i * h
            py = min_y + j * h
            p = Point2D(px, py)
            
            for k in range(len(polygon)):
                p1 = polygon[k]
                p2 = polygon[(k + 1) % len(polygon)]
                dist = dist_point_to_segment(p, p1, p2)
                if dist < h * 1.5:
                    grid[i][j] = min(grid[i][j], dist)

    # 3. Fast Sweeping Method
    def solve_local(a, b, h):
        if abs(a - b) >= h:
            return min(a, b) + h
        else:
            return (a + b + math.sqrt(2 * h * h - (a - b)**2)) / 2.0

    sweeps = [
        (range(nx), range(ny)),
        (range(nx-1, -1, -1), range(ny)),
        (range(nx), range(ny-1, -1, -1)),
        (range(nx-1, -1, -1), range(ny-1, -1, -1)),
    ]

    for _ in range(2): 
        for x_range, y_range in sweeps:
            for i in x_range:
                for j in y_range:
                    u_left = grid[i-1][j] if i > 0 else float('inf')
                    u_right = grid[i+1][j] if i < nx-1 else float('inf')
                    u_bottom = grid[i][j-1] if j > 0 else float('inf')
                    u_top = grid[i][j+1] if j < ny-1 else float('inf')
                    
                    a = min(u_left, u_right)
                    b = min(u_bottom, u_top)
                    
                    new_val = solve_local(a, b, h)
                    grid[i][j] = min(grid[i][j], new_val)

    return grid, (min_x, max_x, min_y, max_y)


def visualize_distance_map_svg(grid: List[List[float]], extent: Tuple[float, float, float, float]) -> str:
    """Visualizes the distance map as an SVG heatmap."""
    nx = len(grid)
    ny = len(grid[0])
    
    max_dist = 0.0
    for i in range(nx):
        for j in range(ny):
            if grid[i][j] != float('inf'):
                max_dist = max(max_dist, grid[i][j])
    
    cell_size = 5
    width = nx * cell_size
    height = ny * cell_size
    
    svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
    
    for i in range(nx):
        for j in range(ny):
            d = grid[i][j]
            val = int(255 * (d / max_dist)) if max_dist > 0 else 0
            color = f"rgb({val}, {100}, {255-val})"
            svg.append(f'  <rect x="{i*cell_size}" y="{(ny-1-j)*cell_size}" width="{cell_size}" height="{cell_size}" fill="{color}" />')
    
    svg.append('</svg>')
    return "\n".join(svg)


__all__ = ["solve_distance_map", "visualize_distance_map_svg"]
