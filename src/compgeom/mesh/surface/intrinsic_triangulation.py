"""Intrinsic Delaunay Triangulation using the Intrinsic Edge Flip algorithm."""
from __future__ import annotations
import math
import numpy as np
from typing import List, Tuple, Optional, Dict, Set
from collections import deque

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh, Vertex, Face, HalfEdge
from compgeom.kernel import Point3D

class IntrinsicTriangulation:
    """
    Represents an intrinsic triangulation of a 3D manifold mesh.
    Vertices are fixed at their original 3D coordinates, but edges are geodesics
    on the surface represented solely by their lengths.
    """

    def __init__(self, he_mesh: HalfEdgeMesh):
        self.he_mesh = he_mesh
        self.edge_lengths: Dict[int, float] = {} # Maps half-edge ID to length
        self._initialize_lengths()

    @classmethod
    def from_mesh(cls, mesh: TriMesh) -> IntrinsicTriangulation:
        """Initializes an intrinsic triangulation from a standard TriMesh."""
        he_mesh = HalfEdgeMesh.from_triangle_mesh(mesh)
        return cls(he_mesh)

    def _initialize_lengths(self):
        """Sets initial edge lengths based on Euclidean distances in 3D."""
        for he in self.he_mesh.edges:
            v1 = he.vertex.point
            v2 = he.twin.vertex.point if he.twin else he.next.next.vertex.point # Fallback for boundary
            
            # More robustly: v1 is start, he.next.vertex is end of this specific half-edge
            p1 = he.vertex.point
            p2 = he.next.vertex.point
            dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (getattr(p1, 'z', 0.0) - getattr(p2, 'z', 0.0))**2)
            self.edge_lengths[he.idx] = dist

    def _get_length(self, he: HalfEdge) -> float:
        return self.edge_lengths.get(he.idx, 0.0)

    def _get_opposite_angle(self, he: HalfEdge) -> float:
        """Calculates the angle opposite to half-edge 'he' using the Law of Cosines."""
        # Triangle vertices: he.vertex, he.next.vertex, he.next.next.vertex
        # Edge lengths: 
        # L_opposite = length(he)
        # L_left = length(he.next)
        # L_right = length(he.next.next)
        
        l_opp = self._get_length(he)
        l_next = self._get_length(he.next)
        l_prev = self._get_length(he.next.next)
        
        # Angle at vertex he.next.next.vertex opposite to 'he'
        # cos(A) = (b^2 + c^2 - a^2) / 2bc
        denom = 2 * l_next * l_prev
        if abs(denom) < 1e-12: return 0.0
        
        val = (l_next**2 + l_prev**2 - l_opp**2) / denom
        return math.acos(max(-1.0, min(1.0, val)))

    def is_delaunay(self, he: HalfEdge) -> bool:
        """Checks if an edge is intrinsically Delaunay."""
        if not he.twin:
            return True # Boundary edges are always Delaunay
            
        angle_sum = self._get_opposite_angle(he) + self._get_opposite_angle(he.twin)
        return angle_sum <= math.pi + 1e-9

    def flip_edge(self, he: HalfEdge):
        """
        Performs an intrinsic edge flip.
        Updates connectivity and computes the new geodesic edge length.
        """
        if not he.twin: return
        
        # 1. Identify quadrilateral vertices and current edges
        # Triangle 1: (v_i, v_j, v_k) - he is (v_i -> v_j)
        # Triangle 2: (v_j, v_i, v_l) - he.twin is (v_j -> v_i)
        
        h_ij = he
        h_jk = he.next
        h_ki = he.next.next
        
        h_ji = he.twin
        h_il = h_ji.next
        h_lj = h_ji.next.next
        
        v_i = h_ij.vertex
        v_j = h_ji.vertex
        v_k = h_jk.next.vertex
        v_l = h_il.next.vertex
        
        # 2. Compute new edge length L_kl using law of cosines in the quad
        # We can treat the quad as two triangles sharing edge ij.
        # Use the polar coordinates of k and l relative to edge ij.
        l_ij = self._get_length(h_ij)
        l_jk = self._get_length(h_jk)
        l_ki = self._get_length(h_ki)
        l_il = self._get_length(h_il)
        l_lj = self._get_length(h_lj)
        
        # Angle at v_i in tri(ijk)
        cos_i_ijk = (l_ij**2 + l_ki**2 - l_jk**2) / (2 * l_ij * l_ki)
        sin_i_ijk = math.sqrt(max(0.0, 1.0 - cos_i_ijk**2))
        
        # Angle at v_i in tri(ilj)
        cos_i_ilj = (l_ij**2 + l_il**2 - l_lj**2) / (2 * l_ij * l_il)
        sin_i_ilj = math.sqrt(max(0.0, 1.0 - cos_i_ilj**2))
        
        # Coordinates of k and l in 2D plane (v_i at origin, v_j on X axis)
        kx, ky = l_ki * cos_i_ijk, l_ki * sin_i_ijk
        lx, ly = l_il * cos_i_ilj, -l_il * sin_i_ilj # l is on the other side of edge ij
        
        l_new = math.sqrt((kx - lx)**2 + (ky - ly)**2)
        
        # 3. Update Topology
        # New Tri 1: h_kl (h_ij), h_lj, h_jk
        # New Tri 2: h_lk (h_ji), h_ki, h_il
        
        # Update vertices
        h_ij.vertex = v_k
        h_ji.vertex = v_l
        
        # Re-link next pointers
        h_ij.next = h_lj
        h_lj.next = h_jk
        h_jk.next = h_ij
        
        h_ji.next = h_ki
        h_ki.next = h_il
        h_il.next = h_ji
        
        # Update faces
        f1 = h_ij.face
        f2 = h_ji.face
        
        h_ij.face = f1
        h_lj.face = f1
        h_jk.face = f1
        
        h_ji.face = f2
        h_ki.face = f2
        h_il.face = f2
        
        f1.edge = h_ij
        f2.edge = h_ji
        
        # Ensure vertices point to a valid outgoing half-edge
        v_i.edge = h_il
        v_j.edge = h_jk
        v_k.edge = h_ki
        v_l.edge = h_lj
        
        # 4. Update Lengths
        self.edge_lengths[h_ij.idx] = l_new
        self.edge_lengths[h_ji.idx] = l_new

    def make_delaunay(self):
        """Flips all non-Delaunay edges until convergence."""
        queue = deque()
        in_queue = set()
        
        # Initial check
        for he in self.he_mesh.edges:
            # Only process one half-edge per edge
            if he.twin and he.idx < he.twin.idx:
                if not self.is_delaunay(he):
                    queue.append(he)
                    in_queue.add(he.idx)
                    
        while queue:
            he = queue.popleft()
            in_queue.remove(he.idx)
            
            if not self.is_delaunay(he):
                # 1. Flip
                self.flip_edge(he)
                
                # 2. Re-check surrounding edges
                # Neighbors are the 4 edges of the quad (excluding the flipped one)
                neighbors = [he.next, he.next.next, he.twin.next, he.twin.next.next]
                for n in neighbors:
                    if n.twin:
                        # Canonical half-edge for the edge
                        canonical = n if n.idx < n.twin.idx else n.twin
                        if canonical.idx not in in_queue:
                            if not self.is_delaunay(canonical):
                                queue.append(canonical)
                                in_queue.add(canonical.idx)

    def to_mesh(self) -> TriMesh:
        """Exports the intrinsic triangulation back to a TriMesh."""
        return self.he_mesh.to_triangle_mesh()
