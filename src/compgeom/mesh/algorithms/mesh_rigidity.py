"""Calculates the rigidity of a mesh with fixed and moving nodes."""

import numpy as np
from typing import List, Tuple, Set
from compgeom.mesh import Mesh, TriMesh, MeshTopology
from compgeom.kernel import Point3D

class MeshRigidity:
    """Provides algorithms for analyzing mesh rigidity and constraints."""

    @staticmethod
    def get_edges(mesh: Mesh) -> Set[Tuple[int, int]]:
        """Extracts unique edges from the mesh topology."""
        edges = set()
        if hasattr(mesh, 'faces'):
            for face in mesh.faces:
                for i in range(len(face)):
                    u, v = face[i], face[(i + 1) % len(face)]
                    edges.add(tuple(sorted((u, v))))
        elif hasattr(mesh, 'topology'):
            # Fallback to topology if available
            n_vertices = len(mesh.vertices)
            topo = MeshTopology(mesh)
            for i in range(n_vertices):
                neighbors = topo.vertex_neighbors(i)
                for neighbor in neighbors:
                    edges.add(tuple(sorted((i, neighbor))))
        return edges

    @staticmethod
    def calculate_rigidity_matrix(
        mesh: Mesh, 
        fixed_node_indices: List[int], 
        moving_node_idx: int = -1
    ) -> np.ndarray:
        """
        Constructs the reduced rigidity matrix for the free nodes.
        
        The rigidity matrix R has rows for each edge and columns for each free coordinate.
        A node is 'free' if it is not in fixed_node_indices and is not moving_node_idx.
        
        Args:
            mesh: The mesh object.
            fixed_node_indices: Indices of nodes that are permanently fixed.
            moving_node_idx: Index of the node that is moved to a target position (also treated as fixed for rigidity).
            
        Returns:
            The reduced rigidity matrix (M x 3*N_free).
        """
        vertices = mesh.vertices
        n_vertices = len(vertices)
        edges = sorted(list(MeshRigidity.get_edges(mesh)))
        n_edges = len(edges)
        
        all_fixed = set(fixed_node_indices)
        if moving_node_idx >= 0:
            all_fixed.add(moving_node_idx)
            
        free_nodes = [i for i in range(n_vertices) if i not in all_fixed]
        node_to_col_idx = {node_idx: i for i, node_idx in enumerate(free_nodes)}
        n_free = len(free_nodes)
        
        # Rigidity matrix for 3D
        # Each free node has 3 DOFs (x, y, z)
        R = np.zeros((n_edges, 3 * n_free))
        
        for e_idx, (u, v) in enumerate(edges):
            p_u = vertices[u]
            p_v = vertices[v]
            
            # Vector from v to u
            diff = np.array([p_u.x - p_v.x, p_u.y - p_v.y, p_u.z - p_v.z])
            
            if u in node_to_col_idx:
                col_u = node_to_col_idx[u]
                R[e_idx, 3 * col_u : 3 * col_u + 3] = diff
                
            if v in node_to_col_idx:
                col_v = node_to_col_idx[v]
                # Row for (u,v) has (p_u - p_v) at u and (p_v - p_u) at v
                R[e_idx, 3 * col_v : 3 * col_v + 3] = -diff
                
        return R

    @staticmethod
    def is_rigid(
        mesh: Mesh, 
        fixed_node_indices: List[int], 
        moving_node_idx: int = -1
    ) -> bool:
        """
        Determines if the mesh is infinitesimally rigid given the constraints.
        
        Args:
            mesh: The mesh object.
            fixed_node_indices: Indices of nodes that are permanently fixed.
            moving_node_idx: Index of the node being moved.
            
        Returns:
            True if the graph is rigid, False otherwise.
        """
        vertices = mesh.vertices
        n_vertices = len(vertices)
        
        all_fixed = set(fixed_node_indices)
        if moving_node_idx >= 0:
            all_fixed.add(moving_node_idx)
            
        free_nodes = [i for i in range(n_vertices) if i not in all_fixed]
        n_free = len(free_nodes)
        
        if n_free == 0:
            return True # Everything is fixed
            
        R = MeshRigidity.calculate_rigidity_matrix(mesh, fixed_node_indices, moving_node_idx)
        
        # The system is rigid if the rank of the rigidity matrix equals the number of degrees of freedom.
        # Required rank is 3 * n_free.
        rank = np.linalg.matrix_rank(R)
        
        return rank >= 3 * n_free

    @staticmethod
    def check_movement_feasibility(
        mesh: Mesh,
        fixed_node_indices: List[int],
        moving_node_idx: int,
        target_position: Tuple[float, float, float]
    ) -> Tuple[bool, bool]:
        """
        Checks if moving a node to a target position is infinitesimally feasible
        and if the resulting configuration is rigid.
        
        Args:
            mesh: The mesh object.
            fixed_node_indices: Indices of nodes that are permanently fixed.
            moving_node_idx: Index of the node that is moved.
            target_position: (x, y, z) of the target.
            
        Returns:
            A tuple (is_feasible, is_rigid).
            is_feasible: True if the movement doesn't violate infinitesimal edge length constraints.
            is_rigid: True if the configuration (with moving node at target) is rigid.
        """
        vertices = mesh.vertices
        p_m = vertices[moving_node_idx]
        dp_m = np.array([
            target_position[0] - p_m.x,
            target_position[1] - p_m.y,
            target_position[2] - p_m.z
        ])
        
        # If no movement, just check current rigidity
        if np.allclose(dp_m, 0):
            rigid = MeshRigidity.is_rigid(mesh, fixed_node_indices, moving_node_idx)
            return True, rigid
            
        edges = sorted(list(MeshRigidity.get_edges(mesh)))
        n_edges = len(edges)
        
        fixed_set = set(fixed_node_indices)
        free_nodes = [i for i in range(len(vertices)) if i not in fixed_set and i != moving_node_idx]
        n_free = len(free_nodes)
        node_to_col_idx = {node_idx: i for i, node_idx in enumerate(free_nodes)}
        
        # R_red * dp_free = b
        R_red = MeshRigidity.calculate_rigidity_matrix(mesh, fixed_node_indices, moving_node_idx)
        b = np.zeros(n_edges)
        
        for e_idx, (u, v) in enumerate(edges):
            p_u = vertices[u]
            p_v = vertices[v]
            diff = np.array([p_u.x - p_v.x, p_u.y - p_v.y, p_u.z - p_v.z])
            
            # Constraint: (p_u - p_v) . (dp_u - dp_v) = 0
            if u == moving_node_idx:
                # diff . (dp_m - dp_v) = 0  =>  -diff . dp_v = -diff . dp_m
                # Wait, if v is free, it's in R_red.
                # If v is fixed, dp_v = 0.
                b[e_idx] = -np.dot(diff, dp_m)
            elif v == moving_node_idx:
                # diff . (dp_u - dp_m) = 0  =>  diff . dp_u = diff . dp_m
                b[e_idx] = np.dot(diff, dp_m)
            else:
                # No moving node involved in this edge constraint RHS
                b[e_idx] = 0.0
                
        # Check if b is in column space of R_red
        # We can use least squares and check residual
        if R_red.shape[1] > 0:
            dp_free, residuals, rank, s = np.linalg.lstsq(R_red, b, rcond=None)
            if residuals.size > 0:
                is_feasible = residuals[0] < 1e-10
            else:
                # If it's underdetermined, residuals might be empty but it could still be feasible
                # Check if R_red @ dp_free is close to b
                is_feasible = np.allclose(R_red @ dp_free, b)
            
            is_rigid = rank >= 3 * n_free
        else:
            # No free nodes. All edges must satisfy constraint directly.
            is_feasible = np.all(np.abs(b) < 1e-10)
            is_rigid = True
            
        return is_feasible, is_rigid

    @staticmethod
    def analyze_degrees_of_freedom(
        mesh: Mesh, 
        fixed_node_indices: List[int], 
        moving_node_idx: int = -1
    ) -> int:
        """
        Calculates the number of internal degrees of freedom remaining in the mesh.
        
        Returns:
            The number of infinitesimal DOFs. 0 means the mesh is rigid.
        """
        vertices = mesh.vertices
        n_vertices = len(vertices)
        
        all_fixed = set(fixed_node_indices)
        if moving_node_idx >= 0:
            all_fixed.add(moving_node_idx)
            
        free_nodes = [i for i in range(n_vertices) if i not in all_fixed]
        n_free = len(free_nodes)
        
        if n_free == 0:
            return 0
            
        R = MeshRigidity.calculate_rigidity_matrix(mesh, fixed_node_indices, moving_node_idx)
        rank = np.linalg.matrix_rank(R)
        
        return 3 * n_free - rank
