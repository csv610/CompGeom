"""Point winding number algorithm for polygons."""

from __future__ import annotations
import math
from typing import List, Union, Tuple

from compgeom.mesh.surfmesh.polymesh.polymesh import PolygonMesh
from compgeom.kernel import Point2D, Point3D


def point_winding_number(point: Union[Point2D, Point3D], polygon_vertices: List[Union[Point2D, Point3D]]) -> int:
    """
    Calculates the winding number of a point with respect to a polygon in 2D.
    
    A winding number of 0 means the point is outside the polygon.
    Non-zero means the point is inside.
    
    Args:
        point: The point to test.
        polygon_vertices: Ordered list of vertices defining the polygon.
        
    Returns:
        The winding number (integer).
    """
    wn = 0
    n = len(polygon_vertices)
    
    px, py = point.x, point.y
    
    for i in range(n):
        v1 = polygon_vertices[i]
        v2 = polygon_vertices[(i + 1) % n]
        
        v1x, v1y = v1.x, v1.y
        v2x, v2y = v2.x, v2.y
        
        if v1y <= py:
            if v2y > py: # Upward crossing
                # Check if point is to the left of the edge
                if is_left(v1x, v1y, v2x, v2y, px, py) > 0:
                    wn += 1
        else:
            if v2y <= py: # Downward crossing
                # Check if point is to the right of the edge
                if is_left(v1x, v1y, v2x, v2y, px, py) < 0:
                    wn -= 1
                    
    return wn


def is_left(v1x: float, v1y: float, v2x: float, v2y: float, px: float, py: float) -> float:
    """
    Determines if a point is to the left, right, or on an infinite line.
    
    Returns:
        > 0 for P left of the line through V1 and V2
        = 0 for P on the line
        < 0 for P right of the line
    """
    return (v2x - v1x) * (py - v1y) - (px - v1x) * (v2y - v1y)


def is_point_inside_polygon(point: Union[Point2D, Point3D], polygon_vertices: List[Union[Point2D, Point3D]]) -> bool:
    """Returns True if the point is inside the polygon (non-zero winding number)."""
    return point_winding_number(point, polygon_vertices) != 0


class PolygonWinding:
    """Helper for winding number queries on PolygonMesh objects."""
    
    @staticmethod
    def winding_number(point: Union[Point2D, Point3D], mesh: PolygonMesh, face_idx: int) -> int:
        """Calculates winding number for a specific face in a PolygonMesh."""
        face = mesh.faces[face_idx]
        vertices = [mesh.vertices[i] for i in face]
        return point_winding_number(point, vertices)
