from __future__ import annotations
import math
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict

from compgeom.kernel import Point3D, Plane
from compgeom.mesh.volume.polyhedral_mesh import PolyhedralMesh
from compgeom.mesh.volume.voromesh.voronoi_clipping import clip_polyhedron_by_plane

class BoundedVoronoi3D:
    """
    Computes a bounded Voronoi diagram for a set of points in 3D.
    Clipping is performed against a specified convex boundary.
    """

    def __init__(self, boundary_planes: List[Plane], boundary_vertices: List[Point3D], boundary_faces: List[List[int]]):
        self.boundary_planes = boundary_planes
        self.initial_vertices = boundary_vertices
        self.initial_faces = boundary_faces

    @classmethod
    def from_box(cls, min_p: Point3D, max_p: Point3D) -> BoundedVoronoi3D:
        """Creates a BoundedVoronoi3D with an axis-aligned box boundary."""
        # 8 vertices
        v = [
            Point3D(min_p.x, min_p.y, min_p.z),
            Point3D(max_p.x, min_p.y, min_p.z),
            Point3D(max_p.x, max_p.y, min_p.z),
            Point3D(min_p.x, max_p.y, min_p.z),
            Point3D(min_p.x, min_p.y, max_p.z),
            Point3D(max_p.x, min_p.y, max_p.z),
            Point3D(max_p.x, max_p.y, max_p.z),
            Point3D(min_p.x, max_p.y, max_p.z),
        ]
        # 6 faces
        f = [
            [0, 3, 2, 1], # bottom (-z)
            [4, 5, 6, 7], # top (+z)
            [0, 1, 5, 4], # front (-y)
            [2, 3, 7, 6], # back (+y)
            [0, 4, 7, 3], # left (-x)
            [1, 2, 6, 5], # right (+x)
        ]
        # 6 planes (pointing inwards)
        planes = [
            Plane(Point3D(0, 0, 1), -min_p.z),  # bottom
            Plane(Point3D(0, 0, -1), max_p.z),   # top
            Plane(Point3D(0, 1, 0), -min_p.y),  # front
            Plane(Point3D(0, -1, 0), max_p.y),  # back
            Plane(Point3D(1, 0, 0), -min_p.x),  # left
            Plane(Point3D(-1, 0, 0), max_p.x),  # right
        ]
        return cls(planes, v, f)

    @classmethod
    def from_sphere(cls, center: Point3D, radius: float, num_planes: int = 12) -> BoundedVoronoi3D:
        """
        Creates a BoundedVoronoi3D with a sphere boundary.
        The sphere is approximated by num_planes tangent planes.
        """
        planes = []
        # We'll use a simple approximation: distribute points on sphere and create tangent planes
        phi = math.pi * (3.0 - math.sqrt(5.0)) # golden angle
        for i in range(num_planes):
            y = 1 - (i / float(num_planes - 1)) * 2
            rad = math.sqrt(1 - y * y)
            theta = phi * i
            x = math.cos(theta) * rad
            z = math.sin(theta) * rad
            
            normal = Point3D(x, y, z)
            # Plane is at distance 'radius' from center
            point_on_plane = center + normal * radius
            # Normal points inwards for our clipper (plane(p) >= 0 is keep side)
            inward_normal = normal * -1.0
            planes.append(Plane.from_point_and_normal(point_on_plane, inward_normal))
        
        # For sphere, we'll start with a huge box and clip it with these planes
        # to get the initial polyhedron.
        huge = radius * 2.0
        box = cls.from_box(center - Point3D(huge, huge, huge), center + Point3D(huge, huge, huge))
        v, f = box.initial_vertices, box.initial_faces
        for p in planes:
            v, f = clip_polyhedron_by_plane(v, f, p)
            
        return cls(planes, v, f)

    @classmethod
    def from_cylinder(cls, center: Point3D, radius: float, height: float, num_sides: int = 8) -> BoundedVoronoi3D:
        """
        Creates a BoundedVoronoi3D with a cylinder boundary.
        The cylinder is approximated by a prism with num_sides.
        """
        # Top and bottom planes
        top_p = Plane.from_point_and_normal(center + Point3D(0, 0, height/2), Point3D(0, 0, -1))
        bot_p = Plane.from_point_and_normal(center - Point3D(0, 0, height/2), Point3D(0, 0, 1))
        
        side_planes = []
        for i in range(num_sides):
            angle = 2 * math.pi * i / num_sides
            x = math.cos(angle)
            y = math.sin(angle)
            normal = Point3D(x, y, 0)
            point_on_side = center + normal * radius
            side_planes.append(Plane.from_point_and_normal(point_on_side, normal * -1.0))
            
        # Initial huge box to clip
        huge = max(radius, height) * 2.0
        box = cls.from_box(center - Point3D(huge, huge, huge), center + Point3D(huge, huge, huge))
        v, f = box.initial_vertices, box.initial_faces
        for p in [top_p, bot_p] + side_planes:
            v, f = clip_polyhedron_by_plane(v, f, p)
            
        return cls([top_p, bot_p] + side_planes, v, f)

    def compute(self, points: List[Point3D]) -> PolyhedralMesh:
        """
        Computes the clipped Voronoi cells for each point.
        """
        if not points:
            return PolyhedralMesh([], [], seeds=[])

        global_vertices = []
        all_cells = []
        
        for i, p_i in enumerate(points):
            # Start with the boundary polyhedron
            curr_v = list(self.initial_vertices)
            curr_f = list(self.initial_faces)
            
            # Clip with all other points (O(N^2))
            for j, p_j in enumerate(points):
                if i == j: continue
                # Bisector plane between p_i and p_j
                mid = (p_i + p_j) * 0.5
                normal = p_i - p_j
                plane = Plane.from_point_and_normal(mid, normal)
                
                curr_v, curr_f = clip_polyhedron_by_plane(curr_v, curr_f, plane)
                if not curr_v:
                    break
            
            if curr_v:
                offset = len(global_vertices)
                global_vertices.extend(curr_v)
                new_cell_faces = [[idx + offset for idx in face] for face in curr_f]
                all_cells.append(new_cell_faces)
            else:
                all_cells.append([])

        return PolyhedralMesh(global_vertices, all_cells, seeds=points)
