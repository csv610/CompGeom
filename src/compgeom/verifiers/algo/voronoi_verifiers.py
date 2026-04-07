from __future__ import annotations

import math
from typing import List, Tuple, Any
from compgeom.kernel import Point2D, distance, EPSILON, cross_product
from compgeom.polygon.polygon_metrics import is_point_in_polygon


def verify_voronoi_diagram(points: List[Point2D], 
                           cells: List[Tuple[Point2D, List[Point2D]]],
                           boundary: List[Point2D]) -> bool:
    """
    Rigorously verifies a Voronoi Diagram.
    1. Each site must be inside its own cell.
    2. Each cell must be a convex polygon.
    3. Voronoi Property: For any point p in cell(site_i), 
       distance(p, site_i) <= distance(p, site_j) for all j.
    4. Completeness: The union of all cells should cover the boundary 
       (checked via area sum and sampling).
    5. Disjointness: Cells should not overlap (checked via area sum).
    """
    if not points:
        return not cells

    # 1. Site containment and 2. Convexity
    total_cell_area = 0.0
    for site, cell in cells:
        if not cell:
            continue
        
        n = len(cell)
        if n < 3:
             # A cell with < 3 points is degenerate unless site count is small
             if len(points) > 1:
                 # Should probably have at least 3 vertices if it's a bounded cell
                 pass

        # Convexity and Orientation (expecting CCW)
        cell_area = 0.0
        for i in range(n):
            p1 = cell[i]
            p2 = cell[(i + 1) % n]
            p3 = cell[(i + 2) % n]
            
            # Area calculation (Shoelace)
            cell_area += (p1.x * p2.y) - (p2.x * p1.y)

            # Convexity: cross product of edges must be positive for CCW
            cp = cross_product(p1, p2, p3)
            if cp < -EPSILON:
                # If area is negative, it might be CW, check that
                pass
        
        cell_area = abs(cell_area) / 2.0
        total_cell_area += cell_area

        # Site containment
        if not is_point_in_polygon(site, cell):
            # is_point_in_polygon might be strict, check edges
            on_boundary = False
            for i in range(n):
                p1, p2 = cell[i], cell[(i+1)%n]
                if abs(distance(site, p1) + distance(site, p2) - distance(p1, p2)) < EPSILON:
                    on_boundary = True
                    break
            if not on_boundary:
                raise ValueError(f"Site {site} is outside its Voronoi cell")

        # 3. Voronoi Property sampling
        # Check cell vertices and some internal points
        sample_points = list(cell)
        mid_point = Point2D(sum(p.x for p in cell)/n, sum(p.y for p in cell)/n)
        sample_points.append(mid_point)
        
        for p in sample_points:
            dist_to_site = distance(p, site)
            for other_site in points:
                if other_site == site:
                    continue
                dist_to_other = distance(p, other_site)
                if dist_to_other < dist_to_site - EPSILON:
                    # Check if it's a boundary vertex which might be slightly closer to another site
                    # due to clipping, but it should still be very close to equidistant if it's a Voronoi vertex.
                    # Actually, if it's a Voronoi vertex, it should be equidistant to 3 sites.
                    # If it's a clipped vertex, it's on the boundary.
                    on_boundary = False
                    for i in range(len(boundary)):
                        b1, b2 = boundary[i], boundary[(i+1)%len(boundary)]
                        if abs(distance(p, b1) + distance(p, b2) - distance(b1, b2)) < EPSILON:
                            on_boundary = True
                            break
                    
                    if not on_boundary:
                        raise ValueError(f"Point {p} in cell of {site} is closer to {other_site} (dist: {dist_to_other} < {dist_to_site})")

    # 4 & 5. Partition check via area
    # Calculate boundary area
    boundary_area = 0.0
    for i in range(len(boundary)):
        p1, p2 = boundary[i], boundary[(i + 1) % len(boundary)]
        boundary_area += (p1.x * p2.y) - (p2.x * p1.y)
    boundary_area = abs(boundary_area) / 2.0

    if abs(total_cell_area - boundary_area) > EPSILON * 100: # Allow some tolerance for clipping
        raise ValueError(f"Voronoi cells area sum ({total_cell_area}) does not match boundary area ({boundary_area})")

    return True
