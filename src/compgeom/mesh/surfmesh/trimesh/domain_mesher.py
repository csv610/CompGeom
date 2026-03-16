"""Generation of random triangle meshes within geometric domains."""

from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING, List, Optional

from ....kernel import Point2D
from .delaunay_triangulation import DelaunayMesher

if TYPE_CHECKING:
    from ...mesh import TriangleMesh


class DomainMesher:
    """Generates random triangle meshes for various 2D shapes with refined boundaries."""

    @staticmethod
    def _discretize_segment(p1: Point2D, p2: Point2D, segment_length: float) -> List[Point2D]:
        """Discretizes a line segment into smaller segments of roughly segment_length."""
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dist = math.sqrt(dx * dx + dy * dy)
        num_segments = max(1, math.ceil(dist / segment_length))
        
        points = []
        for i in range(num_segments + 1): # Include the end point
            t = i / num_segments
            points.append(Point2D(p1.x + t * dx, p1.y + t * dy))
        return points

    @staticmethod
    def _generate_internal_points(
        boundary: List[Point2D], 
        segment_length: float, 
        num_internal_points: Optional[int] = None,
        rejection_ratio: float = 0.001
    ) -> List[Point2D]:
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
        
        from ....polygon.polygon_metrics import is_point_in_polygon
        
        internal_points = []
        buffer = segment_length * 0.5
        
        # Maximize points to ensure we get exactly num_points if possible
        max_trials = num_points * 20
        trials = 0
        
        # Rejection logic is now handled by DelaunayMesher.
        # We generate more points here to allow for rejections later.
        target_count = num_points
        
        while len(internal_points) < target_count and trials < max_trials:
            trials += 1
            p = Point2D(
                random.uniform(min_x + buffer, max_x - buffer),
                random.uniform(min_y + buffer, max_y - buffer)
            )
            if is_point_in_polygon(p, boundary):
                internal_points.append(p)
                    
        return internal_points

    @staticmethod
    def _create_mesh_from_boundary(
        boundary_points: List[Point2D], 
        segment_length: float,
        num_internal_points: Optional[int] = None,
        rejection_ratio: float = 0.001,
        outer_boundary: Optional[List[Point2D]] = None,
        jitter: bool = True
    ) -> TriangleMesh:
        """Helper to triangulate boundary and internal points."""
        # Use the refined boundary points for sampling if no outer_boundary is provided
        search_boundary = outer_boundary or boundary_points
        internal_points = DomainMesher._generate_internal_points(
            search_boundary, segment_length, num_internal_points, rejection_ratio
        )
        
        # Filter duplicates at corners/closure
        seen_coords = set()
        all_points = []
        EPS = 1e-9
        def get_coord_key(p):
            return (round(p.x / EPS), round(p.y / EPS))
            
        for p in boundary_points + internal_points:
            key = get_coord_key(p)
            if key not in seen_coords:
                seen_coords.add(key)
                all_points.append(p)
        
        # Calculate rejection_dist relative to segment_length
        # DelaunayMesher uses its own internal scale for rejection_ratio.
        # To keep it consistent, we'll convert the DomainMesher rejection_ratio.
        min_x = min(p.x for p in all_points)
        max_x = max(p.x for p in all_points)
        min_y = min(p.y for p in all_points)
        max_y = max(p.y for p in all_points)
        scale = max(max_x - min_x, max_y - min_y, 1.0)
        
        # dist_threshold = segment_length * rejection_ratio
        # DelaunayMesher threshold = scale * delaunay_rejection_ratio
        # So delaunay_rejection_ratio = (segment_length * rejection_ratio) / scale
        delaunay_rejection_ratio = (segment_length * rejection_ratio) / scale if rejection_ratio else None
        
        # Generate raw Delaunay triangulation with jitter and rejection delegated to DelaunayMesher
        mesh = DelaunayMesher.triangulate(
            all_points, 
            algorithm="incremental", 
            jitter=jitter, 
            rejection_ratio=delaunay_rejection_ratio
        )
        
        if not outer_boundary:
            return mesh
            
        # Filter triangles whose centroids are outside the outer_boundary
        from ....polygon.polygon_metrics import is_point_in_polygon
        from ...mesh import TriangleMesh
        
        final_faces = []
        for face in mesh.faces:
            v0, v1, v2 = mesh.vertices[face[0]], mesh.vertices[face[1]], mesh.vertices[face[2]]
            centroid = Point2D((v0.x + v1.x + v2.x) / 3.0, (v0.y + v1.y + v2.y) / 3.0)
            if is_point_in_polygon(centroid, outer_boundary):
                final_faces.append(face)
        
        return TriangleMesh(mesh.vertices, final_faces)

    @staticmethod
    def square(
        length: float, 
        boundary_segment_length: float, 
        num_internal_points: Optional[int] = None,
        rejection_ratio: float = 0.001,
        jitter: bool = True
    ) -> TriangleMesh:
        """Generates a refined triangle mesh for a square."""
        corners = [
            Point2D(0, 0),
            Point2D(length, 0),
            Point2D(length, length),
            Point2D(0, length)
        ]
        boundary = []
        for i in range(4):
            boundary.extend(DomainMesher._discretize_segment(corners[i], corners[(i + 1) % 4], boundary_segment_length))
        return DomainMesher._create_mesh_from_boundary(
            boundary, boundary_segment_length, num_internal_points, rejection_ratio, outer_boundary=corners, jitter=jitter
        )

    @staticmethod
    def rectangle(
        width: float, 
        height: float, 
        boundary_segment_length: float, 
        num_internal_points: Optional[int] = None,
        rejection_ratio: float = 0.001,
        jitter: bool = True
    ) -> TriangleMesh:
        """Generates a refined triangle mesh for a rectangle."""
        corners = [
            Point2D(0, 0),
            Point2D(width, 0),
            Point2D(width, height),
            Point2D(0, height)
        ]
        boundary = []
        for i in range(4):
            boundary.extend(DomainMesher._discretize_segment(corners[i], corners[(i + 1) % 4], boundary_segment_length))
        return DomainMesher._create_mesh_from_boundary(
            boundary, boundary_segment_length, num_internal_points, rejection_ratio, outer_boundary=corners, jitter=jitter
        )

    @staticmethod
    def triangle(
        side_length: float, 
        boundary_segment_length: float, 
        num_internal_points: Optional[int] = None,
        rejection_ratio: float = 0.001,
        jitter: bool = True
    ) -> TriangleMesh:
        """Generates a refined triangle mesh for an equilateral triangle."""
        h = side_length * math.sqrt(3) / 2
        corners = [
            Point2D(0, 0),
            Point2D(side_length, 0),
            Point2D(side_length / 2, h)
        ]
        boundary = []
        for i in range(3):
            boundary.extend(DomainMesher._discretize_segment(corners[i], corners[(i + 1) % 3], boundary_segment_length))
        return DomainMesher._create_mesh_from_boundary(
            boundary, boundary_segment_length, num_internal_points, rejection_ratio, outer_boundary=corners, jitter=jitter
        )

    @staticmethod
    def circle(
        radius: float, 
        boundary_segment_length: float, 
        num_internal_points: Optional[int] = None,
        rejection_ratio: float = 0.001,
        jitter: bool = True
    ) -> TriangleMesh:
        """Generates a refined triangle mesh for a circle."""
        num_segments = max(8, math.ceil(2 * math.pi * radius / boundary_segment_length))
        boundary = []
        for i in range(num_segments + 1):
            angle = 2 * math.pi * i / num_segments
            boundary.append(Point2D(radius * math.cos(angle), radius * math.sin(angle)))
        
        # For circle, the outer boundary is the same as the discretization points
        # to ensure it's filtered correctly.
        return DomainMesher._create_mesh_from_boundary(
            boundary, boundary_segment_length, num_internal_points, rejection_ratio, outer_boundary=boundary, jitter=jitter
        )
