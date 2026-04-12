"""Industrial-grade topological manifold repair engine."""

from __future__ import annotations
from collections import defaultdict, deque
from typing import List, Tuple, Set, Dict, Optional
import numpy as np
import math

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh
from compgeom.kernel.predicates import orient3d

class ManifoldValidator:
    """
    Identifies topological defects in a surface mesh.
    Detects:
    - Non-manifold edges (branching)
    - Non-manifold vertices (pinching)
    - Open boundaries (holes)
    - Degenerate elements
    """
    def __init__(self, mesh: TriMesh):
        self.mesh = mesh
        self.edge_to_faces = defaultdict(list)
        self._build_topology()

    def _build_topology(self):
        for i, face in enumerate(self.mesh.faces):
            v = face.v_indices
            for j in range(len(v)):
                u, v_nxt = sorted((v[j], v[(j + 1) % len(v)]))
                self.edge_to_faces[(u, v_nxt)].append(i)

    def find_non_manifold_edges(self) -> List[Tuple[int, int]]:
        """Edges shared by more than 2 faces."""
        return [e for e, faces in self.edge_to_faces.items() if len(faces) > 2]

    def find_boundary_edges(self) -> List[Tuple[int, int]]:
        """Edges shared by exactly 1 face."""
        return [e for e, faces in self.edge_to_faces.items() if len(faces) == 1]

    def find_non_manifold_vertices(self) -> List[int]:
        """Vertices whose incident faces form more than one connected fan."""
        nm_vertices = []
        v2f = defaultdict(list)
        for i, face in enumerate(self.mesh.faces):
            for v in face.v_indices:
                v2f[v].append(i)

        for v, incident_faces in v2f.items():
            if not incident_faces: continue
            
            adj = defaultdict(list)
            for i, f1_idx in enumerate(incident_faces):
                f1_set = set(self.mesh.faces[f1_idx].v_indices)
                for j in range(i + 1, len(incident_faces)):
                    f2_idx = incident_faces[j]
                    f2_set = set(self.mesh.faces[f2_idx].v_indices)
                    if len(f1_set & f2_set) >= 2: # Share an edge
                        adj[f1_idx].append(f2_idx)
                        adj[f2_idx].append(f1_idx)
            
            visited = set()
            num_components = 0
            for f_idx in incident_faces:
                if f_idx not in visited:
                    num_components += 1
                    queue = deque([f_idx])
                    visited.add(f_idx)
                    while queue:
                        curr = queue.popleft()
                        for nxt in adj[curr]:
                            if nxt not in visited:
                                visited.add(nxt)
                                queue.append(nxt)
            
            if num_components > 1:
                nm_vertices.append(v)
        return nm_vertices

    def find_combinatorial_degenerate(self) -> List[int]:
        """Faces with duplicate vertex indices."""
        degenerate = []
        for i, face in enumerate(self.mesh.faces):
            v = face.v_indices
            if len(set(v)) < len(v):
                degenerate.append(i)
        return degenerate

    def find_geometric_degenerate(self, tol: float = 1e-12) -> List[int]:
        """Faces with near-zero area."""
        degenerate = []
        verts = self.mesh.vertices
        for i, face in enumerate(self.mesh.faces):
            v = face.v_indices
            if len(v) < 3:
                degenerate.append(i)
                continue
            
            # Simple area check for triangles (or fan-triangulated polygons)
            area = 0.0
            p0 = verts[v[0]]
            for j in range(1, len(v) - 1):
                p1 = verts[v[j]]
                p2 = verts[v[j+1]]
                
                ux, uy, uz = p1.x - p0.x, p1.y - p0.y, getattr(p1, 'z', 0.0) - getattr(p0, 'z', 0.0)
                vx, vy, vz = p2.x - p0.x, p2.y - p0.y, getattr(p2, 'z', 0.0) - getattr(p0, 'z', 0.0)
                
                # Cross product magnitude
                ax = uy * vz - uz * vy
                ay = uz * vx - ux * vz
                az = ux * vy - uy * vx
                area += 0.5 * math.sqrt(ax*ax + ay*ay + az*az)
            
            if area < tol:
                degenerate.append(i)
        return degenerate

    def find_duplicate_faces(self) -> List[Tuple[int, int]]:
        """Pairs of faces with the same set of vertex indices."""
        face_map = defaultdict(list)
        for i, face in enumerate(self.mesh.faces):
            v = tuple(sorted(face.v_indices))
            face_map[v].append(i)
            
        duplicates = []
        for v, indices in face_map.items():
            if len(indices) > 1:
                for j in range(len(indices)):
                    for k in range(j + 1, len(indices)):
                        duplicates.append((indices[j], indices[k]))
        return duplicates

class ManifoldFixer:
    """
    Fixes topological defects to ensure a valid manifold mesh.
    """
    @staticmethod
    def fix_non_manifold_vertices(mesh: TriMesh) -> TriMesh:
        """
        Splits pinched vertices into multiple unique vertices.
        """
        validator = ManifoldValidator(mesh)
        nm_vertices = validator.find_non_manifold_vertices()
        if not nm_vertices:
            return mesh

        new_vertices = list(mesh.vertices)
        new_faces = [list(f.v_indices) for f in mesh.faces]
        
        v2f = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            for v in face.v_indices:
                v2f[v].append(i)

        for v in nm_vertices:
            incident_faces = v2f[v]
            adj = defaultdict(list)
            for i, f1_idx in enumerate(incident_faces):
                f1_set = set(mesh.faces[f1_idx].v_indices)
                for j in range(i + 1, len(incident_faces)):
                    f2_idx = incident_faces[j]
                    f2_set = set(mesh.faces[f2_idx].v_indices)
                    if len(f1_set & f2_set) >= 2:
                        adj[f1_idx].append(f2_idx)
                        adj[f2_idx].append(f1_idx)
            
            visited = set()
            components = []
            for f_idx in incident_faces:
                if f_idx not in visited:
                    comp = []
                    queue = deque([f_idx])
                    visited.add(f_idx)
                    while queue:
                        curr = queue.popleft()
                        comp.append(curr)
                        for nxt in adj[curr]:
                            if nxt not in visited:
                                visited.add(nxt)
                                queue.append(nxt)
                    components.append(comp)
            
            for comp in components[1:]:
                new_v_idx = len(new_vertices)
                new_vertices.append(mesh.vertices[v])
                for f_idx in comp:
                    f = new_faces[f_idx]
                    for i in range(len(f)):
                        if f[i] == v:
                            f[i] = new_v_idx
                    
        return TriMesh(new_vertices, [tuple(f) for f in new_faces])

    @staticmethod
    def resolve_branching_edges(mesh: TriMesh) -> TriMesh:
        return mesh
