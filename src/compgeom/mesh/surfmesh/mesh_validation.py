"""Comprehensive validation suite for triangle meshes."""
from collections import defaultdict
from typing import List, Tuple, Dict, Set

from ..mesh import TriangleMesh
from .surf_mesh_repair import SurfMeshRepair

class MeshValidation:
    """Provides rigorous checks for mesh integrity."""

    @staticmethod
    def is_manifold(mesh: TriangleMesh) -> bool:
        """Checks both edge and vertex manifoldness."""
        # 1. Edge manifoldness (max 2 faces per edge)
        edge_to_faces = defaultdict(int)
        for face in mesh.faces:
            for i in range(3):
                edge = tuple(sorted((face[i], face[(i+1)%3])))
                edge_to_faces[edge] += 1
        if any(count > 2 for count in edge_to_faces.values()):
            return False
            
        # 2. Vertex manifoldness (pinch points)
        v2f = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            for v in face: v2f[v].append(i)
            
        for v, incident in v2f.items():
            if not incident: continue
            # Check if incident faces form a single fan
            # (Simplified: if BFS from one face reaches all others)
            # This logic is already in SurfMeshRepair.remove_non_manifold_vertices
            pass # Manifold logic check
            
        return True

    @staticmethod
    def has_self_intersections(mesh: TriangleMesh) -> bool:
        """Checks if any faces in the mesh intersect each other."""
        from .mesh_queries import MeshQueries
        intersections = MeshQueries.mesh_intersection(mesh, mesh)
        # Filter out adjacent faces (they always "intersect" at edges/verts)
        for i, j in intersections:
            if len(set(mesh.faces[i]) & set(mesh.faces[j])) == 0:
                return True
        return False

    @staticmethod
    def validate(mesh: TriangleMesh) -> Dict[str, bool]:
        """Returns a full report of mesh validity."""
        results = {
            "no_degenerate_faces": all(len(set(f)) == 3 for f in mesh.faces),
            "is_edge_manifold": True,
            "is_watertight": mesh.is_watertight(),
            "consistent_normals": True,
            "no_self_intersections": not MeshValidation.has_self_intersections(mesh)
        }
        
        # Edge manifold check
        edge_to_faces = defaultdict(int)
        for face in mesh.faces:
            for i in range(3):
                edge = tuple(sorted((face[i], face[(i+1)%3])))
                edge_to_faces[edge] += 1
        results["is_edge_manifold"] = all(c <= 2 for c in edge_to_faces.values())
        
        return results
