"""Generation of random triangle meshes within geometric domains."""

from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING, List, Tuple

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
        for i in range(num_segments):
            t = i / num_segments
            points.append(Point(p1.x + t * dx, p1.y + t * dy))
        return points

    @staticmethod
    def _generate_internal_points(boundary: List[Point], segment_length: float) -> List[Point]:
        """Generates random internal points within the bounding box of the boundary."""
        if not boundary:
            return []
            
        min_x = min(p.x for p in boundary)
        max_x = max(p.x for p in boundary)
        min_y = min(p.y for p in boundary)
        max_y = max(p.y for p in boundary)
        
        # Estimate number of points based on area and segment_length
        area = (max_x - min_x) * (max_y - min_y) # Simple heuristic
        num_points = int(area / (segment_length * segment_length))
        
        from ...polygon.polygon import is_point_in_polygon
        
        internal_points = []
        # Use a bit of a buffer from the boundary
        buffer = segment_length * 0.5
        
        for _ in range(num_points * 2): # Try more points and filter
            p = Point(
                random.uniform(min_x + buffer, max_x - buffer),
                random.uniform(min_y + buffer, max_y - buffer)
            )
            if is_point_in_polygon(p, boundary):
                # Ensure it's not too close to existing points
                too_close = False
                for existing in internal_points + boundary:
                    if math.sqrt((p.x - existing.x)**2 + (p.y - existing.y)**2) < segment_length * 0.8:
                        too_close = True
                        break
                if not too_close:
                    internal_points.append(p)
        return internal_points

    @staticmethod
    def _create_mesh_from_boundary(boundary_points: List[Point], segment_length: float) -> TriangleMesh:
        """Helper to triangulate boundary and internal points."""
        internal_points = DomainMesher._generate_internal_points(boundary_points, segment_length)
        all_points = boundary_points + internal_points
        
        # Using DelaunayMesher to create the mesh. 
        # Since the shapes are convex, standard Delaunay triangulation will 
        # stay within the boundary.
        return DelaunayMesher.triangulate(all_points)

    @staticmethod
    def square(length: float, boundary_segment_length: float) -> TriangleMesh:
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
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length)

    @staticmethod
    def rectangle(width: float, height: float, boundary_segment_length: float) -> TriangleMesh:
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
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length)

    @staticmethod
    def triangle(side_length: float, boundary_segment_length: float) -> TriangleMesh:
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
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length)

    @staticmethod
    def circle(radius: float, boundary_segment_length: float) -> TriangleMesh:
        """Generates a refined triangle mesh for a circle."""
        num_segments = max(8, math.ceil(2 * math.pi * radius / boundary_segment_length))
        boundary = []
        for i in range(num_segments):
            angle = 2 * math.pi * i / num_segments
            boundary.append(Point(radius * math.cos(angle), radius * math.sin(angle)))
        return DomainMesher._create_mesh_from_boundary(boundary, boundary_segment_length)
