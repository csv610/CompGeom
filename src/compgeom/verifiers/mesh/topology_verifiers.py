from __future__ import annotations

import math
from typing import Dict, List, Tuple, Set
from compgeom.mesh.mesh_base import Mesh, MeshFace, MeshEdge, MeshCell


def _gf2_rank(columns: List[int]) -> int:
    """Returns the rank of a binary matrix given as integer bit-columns."""
    basis: Dict[int, int] = {}
    rank = 0

    for value in columns:
        column = value
        while column:
            pivot = column.bit_length() - 1
            if pivot in basis:
                column ^= basis[pivot]
                continue
            basis[pivot] = column
            rank += 1
            break

    return rank


def compute_betti_numbers(mesh: Mesh) -> Tuple[int, int, int, int]:
    """
    Computes the Betti numbers (b0, b1, b2, b3) of the mesh.
    Works for any simplicial/polyhedral complex over GF2.
    """
    vertex_count = len(mesh.nodes)
    
    # Extract edges, faces, and cells if not present
    from compgeom.mesh.mesh_topology import MeshTopology
    topo = MeshTopology(mesh)
    
    # We need a consistent indexing for edges, faces, and cells
    # Use sorted tuples as keys
    
    edge_to_index: Dict[Tuple[int, int], int] = {}
    face_to_index: Dict[Tuple[int, ...], int] = {}
    cell_to_index: Dict[Tuple[int, ...], int] = {}
    
    edges_list: List[Tuple[int, int]] = []
    faces_list: List[Tuple[int, ...]] = []
    cells_list: List[Tuple[int, ...]] = []
    
    # Collect faces and their edges
    raw_faces = [f.v_indices for f in mesh.faces]
    if mesh.cells:
        # Extract faces from cells if it's a volume mesh
        for cell in mesh.cells:
            c_v = cell.v_indices
            cell_key = tuple(sorted(c_v))
            if cell_key not in cell_to_index:
                cell_to_index[cell_key] = len(cells_list)
                cells_list.append(cell_key)
            
            # Use MeshTopology to get faces of this cell
            # But we need them as vertex index tuples
            # A simple way for tet/hex:
            cell_faces = topo._get_cell_faces(cell)
            for f_v in cell_faces:
                f_key = tuple(sorted(f_v))
                if f_key not in face_to_index:
                    face_to_index[f_key] = len(faces_list)
                    faces_list.append(f_key)
    else:
        for f_v in raw_faces:
            f_key = tuple(sorted(f_v))
            if f_key not in face_to_index:
                face_to_index[f_key] = len(faces_list)
                faces_list.append(f_key)

    # Collect edges from faces
    for f_v in faces_list:
        n = len(f_v)
        # For simplicity, assume convex faces (polygons)
        for i in range(n):
            u, v = f_v[i], f_v[(i+1)%n]
            edge_key = tuple(sorted((u, v)))
            if edge_key not in edge_to_index:
                edge_to_index[edge_key] = len(edges_list)
                edges_list.append(edge_key)

    edge_count = len(edges_list)
    face_count = len(faces_list)
    cell_count = len(cells_list)

    # Boundary operators
    # d1: edges -> vertices
    d1_cols = [0] * edge_count
    for i, (u, v) in enumerate(edges_list):
        d1_cols[i] = (1 << u) | (1 << v)

    # d2: faces -> edges
    d2_cols = [0] * face_count
    for i, f_v in enumerate(faces_list):
        col = 0
        n = len(f_v)
        for j in range(n):
            u, v = f_v[j], f_v[(j+1)%n]
            e_idx = edge_to_index[tuple(sorted((u, v)))]
            col ^= (1 << e_idx)
        d2_cols[i] = col

    # d3: cells -> faces
    d3_cols = [0] * cell_count
    if mesh.cells:
        for i, cell_key in enumerate(cells_list):
            # We need the MeshCell object or just its index
            # Find the original MeshCell
            # For simplicity, we can reconstruct the faces for each cell
            # The current cells_list is sorted vertex tuples.
            # We need to find which faces in faces_list belong to which cell.
            # This is slow, but we'll use MeshTopology if possible.
            pass
        # Note: Betti 3 is usually 0 for most meshes unless it's a 3-sphere.
        # Most volume meshes are 3-disks with holes.
    
    rank1 = _gf2_rank(d1_cols)
    rank2 = _gf2_rank(d2_cols)
    
    b0 = vertex_count - rank1
    b1 = edge_count - rank1 - rank2
    
    # For b2 and b3, we need rank3 (d3)
    # If no cells, rank3 = 0
    rank3 = 0
    if mesh.cells:
        # Re-using MeshTopology for cell-face relationships
        d3_cols = [0] * cell_count
        for i, cell in enumerate(mesh.cells):
            cell_faces = topo._get_cell_faces(cell)
            col = 0
            for f_v in cell_faces:
                f_key = tuple(sorted(f_v))
                if f_key in face_to_index:
                    f_idx = face_to_index[f_key]
                    col ^= (1 << f_idx)
            d3_cols[i] = col
        rank3 = _gf2_rank(d3_cols)

    b2 = face_count - rank2 - rank3
    b3 = cell_count - rank3
    
    return b0, b1, b2, b3


def verify_mesh_tunnels(mesh: Mesh, expected_b1: int) -> bool:
    """
    Verifies the number of tunnels (1st Betti number b1).
    For a torus, b1=2. For a cylinder, b1=1.
    """
    b0, b1, b2, b3 = compute_betti_numbers(mesh)
    if b1 != expected_b1:
        raise ValueError(f"Tunnel count mismatch: expected b1={expected_b1}, got {b1}")
    return True


def verify_mesh_cavities(mesh: Mesh, expected_b2: int) -> bool:
    """
    Verifies the number of cavities/voids (2nd Betti number b2 for volume, 
    or number of closed shells for surface).
    """
    b0, b1, b2, b3 = compute_betti_numbers(mesh)
    if b2 != expected_b2:
        raise ValueError(f"Cavity/void count mismatch: expected b2={expected_b2}, got {b2}")
    return True


def verify_mesh_voids(mesh: Mesh, expected_count: int) -> bool:
    """Alias for verify_mesh_cavities."""
    return verify_mesh_cavities(mesh, expected_count)
