"""Generation of random triangle meshes within geometric domains."""

from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING, List, Optional

from ...kernel import Point
from .delaunay_triangulation import DelaunayMesher

if TYPE_CHECKING:
    from ..mesh import TriangleMesh


class DomainMesher:
    """Generates random triangle meshes for various 2D shapes with refined boundaries."""

    @staticmethod
    def _discretize_segment(p1: Point, p2: Point, segment_length: float) -> List[Point]:
        """Discretizes a line segment into smaller segments of roughly segment_length."""
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dist = math.sqrt(dx * dx + dy * dy)
        num_segments = max(1, math.ceil(dist / segment_length))
        
        points = []
        for i in range(num_segments + 1): # Include the end point
            t = i / num_segments
            points.append(Point(p1.x + t * dx, p1.y + t * dy))
        return points

    @staticmethod
    def _generate_internal_points(
        boundary: List[Point], 
        segment_length: float, 
        num_internal_points: Optional[int] = None
    ) -> List[Point]:
        """Generates random internal points within the bounding box of the boundary."""
        if not boundary:
            return []
            
        min_x = min(p.x for p in boundary)
        max_x = max(p.x for p in boundary)
        min_y = min(p.y for p in boundary)
        max_y = max(p.y for p in boundary)
        
        if num_internal_points is None:
            # Estimate number of points based on area and segment_length
            area = (max_x - min_x) * (max_y - min_y) # Simple heuristic
            num_points = int(area / (segment_length * segment_length))
        else:
            num_points = num_internal_points
        
        from ...polygon.polygon import is_point_in_polygon
        
        internal_points = []
        buffer = segment_length * 0.5
        
        # If user specifies many points, we need to be more efficient than rejecting
        # but for simplicity, we'll keep it and just limit trials.
        max_trials = num_points * 5
        trials = 0
        
        while len(internal_points) < num_points and trials < max_trials:
            trials += 1
            p = Point(
                random.uniform(min_x + buffer, max_x - buffer),
                random.uniform(min_y + buffer, max_y - buffer)
            )
            if is_point_in_polygon(p, boundary):
                # Ensure it's not too close to existing points
                # Use a smaller distance threshold if we're hitting a density limit
                too_close = False
                dist_threshold = segment_length * 0.8
                for existing in internal_points:
                    if math.sqrt((p.x - existing.x)**2 + (p.y - existing.y)**2) < dist_threshold:
                        too_close = True
                        break
                if not too_close:
                    internal_points.append(p)
                    
        return internal_points

    @staticmethod
    def _create_mesh_from_boundary(
        boundary_points: List[Point], 
        segment_length: float,
        num_internal_points: Optional[int] = None
    ) -> TriangleMesh:
        """Helper to triangulate boundary and internal points."""
        internal_points = DomainMesher._generate_internal_points(boundary_points, segment_length, num_internal_points)
        
        # Use a list for all_points to maintain stability, but filter duplicates
        seen_coords = set()
        all_points = []
        
        # EPSILON for coordinate comparison
        EPS = 1e-9
        
        def get_coord_key(p):
            return (round(p.x / EPS), round(p.y / EPS))
            
        for p in boundary_points + internal_points:
            key = get_coord_key(p)
            if key not in seen_coords:
                seen_coords.add(key)
                all_points.append(p)
        
        # Using DelaunayMesher to create the mesh. 
        # Since the shapes are convex, standard Delaunay triangulation will 
        # stay within the boundary.
        return DelaunayMesher.triangulate(all_points)

    @staticmethod
    def square(length: float, boundary_segment_length: float, num_internal_points: Optional[int] = None) -> TriangleMesh:
        """Generates a refined triangle mesh for a square."""
        corners = [
            Point(0, 0),
            Point(length, 0),
            Point(length, length),
            Point(0, length)
        ]
        boundary = []
        for i in range(4):
            boundary.extend(DomainMesher._discretize_segment(corners[i], corners[(i + 1) % 4], boundary_segment_length))
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length, num_internal_points)

    @staticmethod
    def rectangle(width: float, height: float, boundary_segment_length: float, num_internal_points: Optional[int] = None) -> TriangleMesh:
        """Generates a refined triangle mesh for a rectangle."""
        corners = [
            Point(0, 0),
            Point(width, 0),
            Point(width, height),
            Point(0, height)
        ]
        boundary = []
        for i in range(4):
            boundary.extend(DomainMesher._discretize_segment(corners[i], corners[(i + 1) % 4], boundary_segment_length))
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length, num_internal_points)

    @staticmethod
    def triangle(side_length: float, boundary_segment_length: float, num_internal_points: Optional[int] = None) -> TriangleMesh:
        """Generates a refined triangle mesh for an equilateral triangle."""
        h = side_length * math.sqrt(3) / 2
        corners = [
            Point(0, 0),
            Point(side_length, 0),
            Point(side_length / 2, h)
        ]
        boundary = []
        for i in range(3):
            boundary.extend(DomainMesher._discretize_segment(corners[i], corners[(i + 1) % 3], boundary_segment_length))
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length, num_internal_points)

    @staticmethod
    def circle(radius: float, boundary_segment_length: float, num_internal_points: Optional[int] = None) -> TriangleMesh:
        """Generates a refined triangle mesh for a circle."""
        num_segments = max(8, math.ceil(2 * math.pi * radius / boundary_segment_length))
        boundary = []
        for i in range(num_segments + 1):
            angle = 2 * math.pi * i / num_segments
            boundary.append(Point(radius * math.cos(angle), radius * math.sin(angle)))
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length, num_internal_points)
