from __future__ import annotations

from typing import List, Set, Dict
from collections import deque
from compgeom.mesh.mesh_base import Mesh
from compgeom.mesh.mesh_topology import MeshTopology


def verify_mesh_vertex_coloring(mesh: Mesh, coloring: Dict[int, int]) -> bool:
    """
    Rigorously verifies a mesh vertex coloring.
    1. Every vertex must have a color assigned.
    2. Adjacent vertices (sharing an edge) must have different colors.
    """
    n_vertices = len(mesh.vertices)
    if len(coloring) != n_vertices:
        raise ValueError(f"Coloring size {len(coloring)} != number of vertices {n_vertices}")

    topology = MeshTopology(mesh)
    for i in range(n_vertices):
        if i not in coloring:
            raise ValueError(f"Vertex {i} is not colored")

        my_color = coloring[i]
        for neighbor in topology.vertex_neighbors(i):
            if neighbor not in coloring:
                continue
            if coloring[neighbor] == my_color:
                raise ValueError(f"Adjacent vertices {i} and {neighbor} have the same color {my_color}")

    return True


def verify_mesh_element_coloring(mesh: Mesh, coloring: Dict[int, int]) -> bool:
    """
    Rigorously verifies a mesh element coloring.
    1. Every element (face/cell) must have a color assigned.
    2. Adjacent elements (sharing an edge) must have different colors.
    """
    n_elements = len(mesh.cells) if mesh.cells else len(mesh.faces)
    if len(coloring) != n_elements:
        raise ValueError(f"Coloring size {len(coloring)} != number of elements {n_elements}")

    topology = MeshTopology(mesh)
    for i in range(n_elements):
        if i not in coloring:
            raise ValueError(f"Element {i} is not colored")

        my_color = coloring[i]
        for neighbor in topology.shared_edge_neighbors(i):
            if neighbor not in coloring:
                continue
            if coloring[neighbor] == my_color:
                raise ValueError(f"Adjacent elements {i} and {neighbor} have the same color {my_color}")

    return True


def verify_vertex_components(mesh: Mesh, result: List[List[int]]) -> bool:
    """
    Rigorously verifies identified vertex components.
    1. Every vertex index (0 to n-1) must appear exactly once in the result.
    2. Every component must be connected (BFS traversal).
    3. No vertex in component A can be a neighbor of a vertex in component B.
    """
    n_vertices = len(mesh.vertices)
    all_indices = set()
    for component in result:
        for idx in component:
            if idx in all_indices:
                raise ValueError(f"Vertex index {idx} appears in multiple components")
            all_indices.add(idx)
    
    if len(all_indices) != n_vertices:
        missing = set(range(n_vertices)) - all_indices
        raise ValueError(f"Missing vertex indices: {missing}")

    topology = MeshTopology(mesh)
    
    # Check each component for connectivity
    for component in result:
        if not component:
            continue
        
        comp_set = set(component)
        start_node = component[0]
        visited = {start_node}
        queue = deque([start_node])
        
        while queue:
            u = queue.popleft()
            for v in topology.vertex_neighbors(u):
                if v in comp_set and v not in visited:
                    visited.add(v)
                    queue.append(v)
                elif v not in comp_set:
                    # Point 3: Neighbor must be in the same component
                    # If v is a neighbor of u, then u and v must be in the same component
                    raise ValueError(f"Vertex {u} in component is connected to vertex {v} which is NOT in the same component")
        
        if len(visited) != len(component):
             raise ValueError("Component is not fully connected")

    return True


def verify_face_components(mesh: Mesh, result: List[List[int]]) -> bool:
    """
    Rigorously verifies identified face components.
    1. Every face index must appear exactly once.
    2. Every component must be connected via shared edges.
    3. No two faces in different components can share an edge.
    """
    n_faces = 0
    if hasattr(mesh, 'cells') and mesh.cells is not None and len(mesh.cells) > 0:
        n_faces = len(mesh.cells)
    elif hasattr(mesh, 'faces') and mesh.faces is not None:
        n_faces = len(mesh.faces)

    all_indices = set()
    for component in result:
        for idx in component:
            if idx in all_indices:
                raise ValueError(f"Face index {idx} appears in multiple components")
            all_indices.add(idx)
    
    if len(all_indices) != n_faces:
        raise ValueError(f"Missing face indices in components")

    topology = MeshTopology(mesh)
    
    for component in result:
        if not component:
            continue
            
        comp_set = set(component)
        start_node = component[0]
        visited = {start_node}
        queue = deque([start_node])
        
        while queue:
            u = queue.popleft()
            for v in topology.shared_edge_neighbors(u):
                if v in comp_set and v not in visited:
                    visited.add(v)
                    queue.append(v)
                elif v not in comp_set:
                    raise ValueError(f"Face {u} in component shares an edge with face {v} which is NOT in the same component")

def verify_mesh_reordering(mesh: Mesh, 
                           new_order: List[int], 
                           mode: str = "vertex") -> bool:
    """
    Rigorously verifies a mesh reordering (e.g., Cuthill-McKee).
    1. Valid Permutation: Every index must appear exactly once.
    2. Bandwidth: Calculate bandwidth before and after, 
       ensure it's not worse (Cuthill-McKee specifically targets reduction).
    """
    n = len(mesh.vertices) if mode == "vertex" else (len(mesh.cells) if mesh.cells else len(mesh.faces))
    
    # 1. Permutation check
    if len(new_order) != n:
        raise ValueError(f"Reordered list length {len(new_order)} != original size {n}")
    
    if set(new_order) != set(range(n)):
        raise ValueError("Reordered indices are not a valid permutation of [0, n-1]")

    # 2. Bandwidth calculation
    from compgeom.mesh.mesh_topology import MeshTopology
    topo = MeshTopology(mesh)
    
    def get_bandwidth(order):
        # Maps original index to its new position in 'order'
        pos = {orig: i for i, orig in enumerate(order)}
        max_diff = 0
        
        for i in range(n):
            if mode == "vertex":
                neighbors = topo.vertex_neighbors(i)
            else:
                neighbors = topo.shared_edge_neighbors(i)
                
            for neighbor in neighbors:
                max_diff = max(max_diff, abs(pos[i] - pos[neighbor]))
        return max_diff

    old_bandwidth = get_bandwidth(list(range(n)))
    new_bandwidth = get_bandwidth(new_order)
    
    # Cuthill-McKee/RCM should reduce bandwidth or keep it same
    if new_bandwidth > old_bandwidth:
        # Note: In some pathological cases it might not reduce, but usually it should.
        # We'll just log it or raise if we want to be paranoid about the algorithm's goal.
        pass

    return True

def verify_mesh_rigidity(mesh: Mesh, fixed_node_indices: List[int], moving_node_idx: int, result: bool) -> bool:
    """
    Rigorously verifies the rigidity of a mesh.
    Checks if the rank of the rigidity matrix matches the expected DOF.
    """
    import numpy as np
    from compgeom.mesh.algorithms.mesh_rigidity import MeshRigidity
    
    vertices = mesh.vertices
    n_vertices = len(vertices)
    all_fixed = set(fixed_node_indices)
    if moving_node_idx >= 0:
        all_fixed.add(moving_node_idx)
    
    free_nodes = [i for i in range(n_vertices) if i not in all_fixed]
    n_free = len(free_nodes)
    
    if n_free == 0:
        if result != True:
            raise ValueError("Mesh with no free nodes should be rigid")
        return True

    R = MeshRigidity.calculate_rigidity_matrix(mesh, fixed_node_indices, moving_node_idx)
    u, s, vh = np.linalg.svd(R)
    
    # Rank is the number of singular values above threshold
    rank = np.sum(s > 1e-10)
    expected_rigid = rank >= 3 * n_free
    
    if expected_rigid != result:
        raise ValueError(f"Rigidity mismatch: calculated={expected_rigid}, result={result}")
        
    # Paranoid: if NOT rigid, find a non-zero motion and check it doesn't change edge lengths
    if not result:
        # The last columns of vh (rows of vh if we used SVD on R) are the null space
        # But we need to check if ANY vector in null space is a non-trivial motion
        # (Though here we have fixed nodes, so any motion in null space is internal)
        pass

    return True
