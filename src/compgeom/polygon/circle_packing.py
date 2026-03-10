"""Circle packing algorithms for arbitrary polygons."""

from __future__ import annotations

import math
from typing import List, Tuple

from ..geo_math.geometry import Point, dist_point_to_segment
from .polygon import is_point_in_polygon, get_polygon_properties


class CirclePacker:
    """Packs circles into a given polygon optimally using a hexagonal grid."""

    @staticmethod
    def pack(polygon: List[Point], radius: float) -> List[Point]:
        """
        Packs circles of a given radius into a polygon using hexagonal packing.
        
        Args:
            polygon: List of Points defining the closed boundary.
            radius: Radius of circles to pack.
            
        Returns:
            List of Points representing the centers of the packed circles.
        """
        if not polygon or radius <= 0:
            return []

        # 1. Find bounding box
        min_x = min(p.x for p in polygon)
        max_x = max(p.x for p in polygon)
        min_y = min(p.y for p in polygon)
        max_y = max(p.y for p in polygon)

        # 2. Generate hexagonal grid
        centers = []
        
        # Horizontal spacing: 2 * radius
        # Vertical spacing: radius * sqrt(3)
        dx = 2 * radius
        dy = radius * math.sqrt(3)
        
        row = 0
        y = min_y + radius
        while y <= max_y - radius:
            # Shift every other row by radius for hexagonal layout
            x_offset = radius if row % 2 == 1 else 0
            x = min_x + radius + x_offset
            
            while x <= max_x - radius:
                center = Point(x, y)
                
                # 3. Check if circle is fully inside
                if CirclePacker._is_circle_inside(center, radius, polygon):
                    centers.append(center)
                
                x += dx
            y += dy
            row += 1
            
        return centers

    @staticmethod
    def optimal_radius(polygon: List[Point], num_circles: int, tolerance: float = 1e-4) -> float:
        """
        Finds the maximum radius such that at least `num_circles` can be packed into the polygon.
        
        Args:
            polygon: List of Points defining the closed boundary.
            num_circles: The target number of circles to pack.
            tolerance: Precision for the binary search.
            
        Returns:
            The maximum radius that fits at least `num_circles` using hexagonal packing.
        """
        if not polygon or num_circles <= 0:
            return 0.0

        min_x = min(p.x for p in polygon)
        max_x = max(p.x for p in polygon)
        min_y = min(p.y for p in polygon)
        max_y = max(p.y for p in polygon)

        # Initial bounds for binary search
        # low = 0: infinitely small circles
        # high: half of the smallest dimension of the bounding box
        low = 0.0
        high = min(max_x - min_x, max_y - min_y) / 2.0
        
        if high <= 0:
            return 0.0

        best_radius = 0.0
        
        # Binary search for the largest radius that fits at least `num_circles`
        # Using 50 iterations as a safety limit if tolerance is extremely small
        for _ in range(50):
            if high - low < tolerance:
                break
                
            mid = (low + high) / 2.0
            centers = CirclePacker.pack(polygon, mid)
            
            if len(centers) >= num_circles:
                best_radius = mid
                low = mid
            else:
                high = mid
                
        return best_radius

    @staticmethod
    def _is_circle_inside(center: Point, radius: float, polygon: List[Point]) -> bool:
        """Checks if a circle is entirely contained within a polygon."""
        # Center must be inside
        if not is_point_in_polygon(center, polygon):
            return False
            
        # Distance to every edge must be >= radius
        n = len(polygon)
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]
            if dist_point_to_segment(center, p1, p2) < radius - 1e-9:
                return False
                
        return True

    @staticmethod
    def calculate_efficiency(polygon: List[Point], centers: List[Point], radius: float) -> float:
        """Calculates the ratio of packed circle area to polygon area."""
        if not centers:
            return 0.0
            
        area, _, _ = get_polygon_properties(polygon)
        
        if area <= 0:
            return 0.0
            
        total_circle_area = len(centers) * math.pi * (radius ** 2)
        return (total_circle_area / area) * 100

    @staticmethod
    def visualize(
        polygon: List[Point], 
        centers: List[Point], 
        radius: float,
        width: int = 800,
        height: int = 600,
        padding: int = 40
    ) -> str:
        """Returns an SVG string showing the polygon and packed circles."""
        min_x = min(p.x for p in polygon)
        max_x = max(p.x for p in polygon)
        min_y = min(p.y for p in polygon)
        max_y = max(p.y for p in polygon)
        
        poly_w = max_x - min_x
        poly_h = max_y - min_y
        
        scale = min((width - 2*padding) / poly_w, (height - 2*padding) / poly_h) if poly_w > 0 and poly_h > 0 else 1.0
        
        def tx(x):
            return padding + (x - min_x) * scale
        
        def ty(y):
            # Invert Y for SVG
            return height - (padding + (y - min_y) * scale)

        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="#f8f9fa" />')
        
        # Draw polygon
        points_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in polygon)
        svg.append(f'<polygon points="{points_str}" fill="white" stroke="black" stroke-width="2" />')
        
        # Draw circles
        r_scaled = radius * scale
        for c in centers:
            svg.append(f'<circle cx="{tx(c.x)}" cy="{ty(c.y)}" r="{r_scaled}" fill="red" fill-opacity="0.4" stroke="darkred" stroke-width="1" />')
            
        svg.append('</svg>')
        return "\n".join(svg)


__all__ = ["CirclePacker"]
