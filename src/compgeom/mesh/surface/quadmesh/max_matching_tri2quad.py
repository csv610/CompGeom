"""Conversion from TriMesh to QuadMesh via maximum cardinality matching."""

from __future__ import annotations
from typing import List, Tuple, Union, Set, Dict

from compgeom.kernel.geometry import Point2D, Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.quadmesh.quadmesh import QuadMesh
from compgeom.mesh.mesh_topology import MeshTopology

class BlossomAlgorithm:
    """Edmonds' blossom algorithm for maximum cardinality matching."""
    def __init__(self, n: int, adj: List[Set[int]]):
        self.n = n
        self.adj = adj
        self.match = [-1] * n
        self.p = [-1] * n
        self.base = list(range(n))
        self.q: List[int] = []
        self.used = [False] * n
        self.blossom = [False] * n

    def lca(self, a: int, b: int) -> int:
        used = [False] * self.n
        while True:
            a = self.base[a]
            used[a] = True
            if self.match[a] == -1:
                break
            a = self.p[self.match[a]]
        while True:
            b = self.base[b]
            if used[b]:
                return b
            b = self.p[self.match[b]]

    def mark_path(self, v: int, b: int, children: int):
        while self.base[v] != b:
            self.blossom[self.base[v]] = self.blossom[self.base[self.match[v]]] = True
            self.p[v] = children
            children = self.match[v]
            v = self.p[self.match[v]]

    def find_path(self, root: int) -> int:
        self.used = [False] * self.n
        self.p = [-1] * self.n
        for i in range(self.n):
            self.base[i] = i
        self.used[root] = True
        self.q = [root]
        qh = 0
        while qh < len(self.q):
            v = self.q[qh]
            qh += 1
            for to in self.adj[v]:
                if self.base[v] == self.base[to] or self.match[v] == to:
                    continue
                if to == root or (self.match[to] != -1 and self.p[self.match[to]] != -1):
                    cur_base = self.lca(v, to)
                    self.blossom = [False] * self.n
                    self.mark_path(v, cur_base, to)
                    self.mark_path(to, cur_base, v)
                    for i in range(self.n):
                        if self.blossom[self.base[i]]:
                            self.base[i] = cur_base
                            if not self.used[i]:
                                self.used[i] = True
                                self.q.append(i)
                elif self.p[to] == -1:
                    self.p[to] = v
                    if self.match[to] == -1:
                        return to
                    to = self.match[to]
                    self.used[to] = True
                    self.q.append(to)
        return -1

    def solve(self) -> List[int]:
        for i in range(self.n):
            if self.match[i] == -1:
                v = self.find_path(i)
                while v != -1:
                    pv = self.p[v]
                    ppv = self.match[pv]
                    self.match[v] = pv
                    self.match[pv] = v
                    v = ppv
        return self.match

class MaxMatchingTriangleToQuadConverter:
    """Converts a TriMesh to a QuadMesh using maximum cardinality matching."""

    @staticmethod
    def convert(mesh: TriMesh) -> QuadMesh:
        """
        Combines pairs of adjacent triangles into quadrilaterals.
        Uses Edmonds' blossom algorithm for maximum cardinality matching.
        """
        num_faces = len(mesh.faces)
        if num_faces == 0:
            return QuadMesh(mesh.vertices, [])
            
        # If the number of triangles is odd, skip the last triangle.
        faces_to_match = num_faces
        if num_faces % 2 != 0:
            faces_to_match = num_faces - 1
            
        if faces_to_match == 0:
            return QuadMesh(mesh.vertices, [])

        adj = []
        topo = MeshTopology(mesh)
        for i in range(faces_to_match):
            neighbors = topo.shared_edge_neighbors(i)
            # Only consider neighbors that are within the faces_to_match range
            valid_neighbors = {n for n in neighbors if n < faces_to_match}
            adj.append(valid_neighbors)
        
        matcher = BlossomAlgorithm(faces_to_match, adj)
        matching = matcher.solve()
        
        quad_faces = []
        processed = [False] * faces_to_match
        
        for i in range(faces_to_match):
            if processed[i]:
                continue
            
            j = matching[i]
            if j != -1:
                t1 = list(mesh.faces[i])
                t2 = list(mesh.faces[j])
                set1 = set(t1)
                set2 = set(t2)
                
                # Identify shared vertices and unique vertices
                shared = set1.intersection(set2)
                if len(shared) == 2:
                    w1 = list(set1 - set2)[0]
                    w2 = list(set2 - set1)[0]
                    
                    # Order t1 such that it starts at its unique vertex w1
                    idx_w1 = t1.index(w1)
                    t1_ordered = t1[idx_w1:] + t1[:idx_w1]
                    
                    # Form a quadrilateral (w1, v1, w2, v2) where (v1, v2) is the shared edge
                    # t1_ordered is (w1, v1, v2)
                    quad_faces.append((t1_ordered[0], t1_ordered[1], w2, t1_ordered[2]))
                    
                processed[i] = True
                processed[j] = True
                
        return QuadMesh(mesh.vertices, quad_faces)
