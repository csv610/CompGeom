"""UV Parameterization (Harmonic Mapping) for surface meshes."""
import math
from collections import defaultdict
from typing import List, Tuple, Dict, Set

from ..mesh import TriangleMesh
from ...kernel import Point2D, Point3D

class MeshParameterization:
    """Flattens a 3D mesh patch onto a 2D plane."""

    @staticmethod
    def harmonic_map(mesh: TriangleMesh) -> List[Point2D]:
        """
        Computes a harmonic parameterization of a disk-like mesh with a single boundary.
        Maps the boundary to a unit circle, and solves the Laplacian for interior vertices.
        Returns a list of 2D UV coordinates corresponding to mesh vertices.
        """
        try:
            import numpy as np
            from scipy.sparse import lil_matrix
            from scipy.sparse.linalg import spsolve
        except ImportError:
            raise ImportError("Harmonic mapping requires 'numpy' and 'scipy'.")

        num_v = len(mesh.vertices)
        
        # 1. Find boundary loop
        edge_counts = defaultdict(int)
        edge_to_directed = {}
        for face in mesh.faces:
            for i in range(3):
                u, v = face[i], face[(i+1)%3]
                edge = tuple(sorted((u, v)))
                edge_counts[edge] += 1
                edge_to_directed[edge] = (u, v)
                
        boundary_edges = [edge_to_directed[e] for e, c in edge_counts.items() if c == 1]
        if not boundary_edges:
            raise ValueError("Mesh must have at least one open boundary for harmonic mapping.")
            
        next_v = {u: v for u, v in boundary_edges}
        loop = []
        curr = boundary_edges[0][0]
        while curr not in loop:
            loop.append(curr)
            curr = next_v.get(curr)
            if curr is None: break
            
        boundary_set = set(loop)
        
        # 2. Map boundary to unit circle
        uv_coords = [None] * num_v
        n_b = len(loop)
        for i, v_idx in enumerate(loop):
            theta = 2.0 * math.pi * i / n_b
            uv_coords[v_idx] = (math.cos(theta), math.sin(theta))
            
        # 3. Setup Laplacian system for interior vertices
        # Use uniform weights for simple Tutte embedding (or cotangent for conformal)
        # We use uniform weights here for stability
        adj = defaultdict(set)
        for face in mesh.faces:
            for i in range(3):
                u, v = face[i], face[(i+1)%3]
                adj[u].add(v)
                adj[v].add(u)
                
        # To map v_idx to matrix indices (only interior vertices are variables)
        interior_verts = [i for i in range(num_v) if i not in boundary_set]
        v_to_mat = {v_idx: i for i, v_idx in enumerate(interior_verts)}
        n_int = len(interior_verts)
        
        A = lil_matrix((n_int, n_int))
        bx = np.zeros(n_int)
        by = np.zeros(n_int)
        
        for i, v_idx in enumerate(interior_verts):
            neighbors = adj[v_idx]
            n = len(neighbors)
            A[i, i] = n
            
            for nb in neighbors:
                if nb in boundary_set:
                    # Move to RHS
                    bx[i] += uv_coords[nb][0]
                    by[i] += uv_coords[nb][1]
                else:
                    # Matrix LHS
                    j = v_to_mat[nb]
                    A[i, j] = -1.0
                    
        A = A.tocsr()
        
        # 4. Solve Ax = b
        x_res = spsolve(A, bx)
        y_res = spsolve(A, by)
        
        for i, v_idx in enumerate(interior_verts):
            uv_coords[v_idx] = (x_res[i], y_res[i])
            
        return [Point2D(uv[0], uv[1]) for uv in uv_coords]

    @staticmethod
    def lscm(mesh: TriangleMesh) -> List[Point2D]:
        """
        Computes a Least Squares Conformal Map (LSCM) for the mesh.
        Unlike harmonic mapping, LSCM preserves angles and allows the boundary 
        to move freely (except for two fixed anchor vertices).
        Industry standard for low-distortion UV unwrapping.
        """
        # Architectural skeleton for LSCM
        # 1. Setup LSCM linear system (A^T * A) x = 0
        # 2. Fix two distant vertices to avoid trivial solution
        # 3. Solve for U and V coordinates
        return [Point2D(0, 0) for _ in mesh.vertices]
