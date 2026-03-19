"""Edge mesh data structure for line segments."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple, Union

from compgeom.mesh.mesh import Mesh, MeshNode, MeshEdge
from compgeom.kernel import Point2D, Point3D


class EdgeMesh(Mesh):
    """A 2D or 3D mesh composed of line segments (edges)."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point2D, Point3D]], 
                 edges: List[Union[MeshEdge, Tuple[int, int]]]):
        if edges and not isinstance(edges[0], MeshEdge):
            edges = [MeshEdge(i, e) for i, e in enumerate(edges)]
        super().__init__(nodes=nodes, edges=edges)

    @classmethod
    def from_segments(cls, segments: List[Tuple[Union[Point2D, Point3D], Union[Point2D, Point3D]]]) -> EdgeMesh:
        """Converts a list of Point segments to an EdgeMesh object."""
        unique_points = []
        point_to_idx = {}
        
        for seg in segments:
            for p in seg:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        nodes = [MeshNode(i, p) for i, p in enumerate(unique_points)]
        edges = [MeshEdge(i, (point_to_idx[seg[0]], point_to_idx[seg[1]])) for i, seg in enumerate(segments)]
            
        return cls(nodes, edges)

    def total_length(self) -> float:
        """Calculates the total length of all edges in the mesh."""
        total = 0.0
        for edge in self.edges:
            u_idx, v_idx = edge.v_indices
            u, v = self.nodes[u_idx].point, self.nodes[v_idx].point
            dist_sq = (u.x - v.x)**2 + (u.y - v.y)**2
            if isinstance(u, Point3D) and isinstance(v, Point3D):
                dist_sq += (u.z - v.z)**2
            total += math.sqrt(dist_sq)
        return total

    def euler_characteristic(self) -> int:
        """Calculates the Euler characteristic (V - E)."""
        v = len(self.nodes)
        e = len(self.edges)
        return v - e
