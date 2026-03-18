"""Refinement algorithms for tetrahedral meshes."""

from __future__ import annotations
from typing import List, Tuple, Dict, Set

from compgeom.kernel import Point3D
from compgeom.mesh.volmesh.tetmesh.tetmesh import TetMesh

def refine_tetmesh_centroid(mesh: TetMesh, element_ids: List[int] = None) -> TetMesh:
    """
    Refines a TetMesh by inserting a point at the centroid of specified tetrahedra.
    If element_ids is None, all tetrahedra are refined.
    Each refined tetrahedron is split into 4 smaller tetrahedra.
    This method is topologically valid and maintains a conforming mesh for local refinement.
    """
    new_vertices = list(mesh.vertices)
    new_cells = []
    
    ids_to_refine = set(element_ids) if element_ids is not None else set(range(len(mesh.cells)))
    
    for i, tet in enumerate(mesh.cells):
        if i in ids_to_refine:
            v_indices = tet.v_indices
            v0, v1, v2, v3 = [mesh.vertices[idx] for idx in v_indices]
            centroid = Point3D(
                (v0.x + v1.x + v2.x + v3.x) / 4.0,
                (v0.y + v1.y + v2.y + v3.y) / 4.0,
                (v0.z + v1.z + v2.z + v3.z) / 4.0
            )
            centroid_idx = len(new_vertices)
            new_vertices.append(centroid)
            
            # Split into 4 tets connecting centroid to each face
            new_cells.append((v_indices[0], v_indices[1], v_indices[2], centroid_idx))
            new_cells.append((v_indices[0], v_indices[1], v_indices[3], centroid_idx))
            new_cells.append((v_indices[0], v_indices[2], v_indices[3], centroid_idx))
            new_cells.append((v_indices[1], v_indices[2], v_indices[3], centroid_idx))
        else:
            new_cells.append(tet.v_indices)
        
    return TetMesh(new_vertices, new_cells)

def refine_tetmesh_midpoint(mesh: TetMesh) -> TetMesh:
    """
    Refines a TetMesh by splitting each edge at its midpoint.
    Each tetrahedron is split into 8 smaller tetrahedra.
    This is a global refinement method.
    """
    new_vertices = list(mesh.vertices)
    edge_to_midpoint: Dict[Tuple[int, int], int] = {}
    
    def get_midpoint(i: int, j: int) -> int:
        edge = tuple(sorted((i, j)))
        if edge in edge_to_midpoint:
            return edge_to_midpoint[edge]
        
        v1, v2 = mesh.vertices[i], mesh.vertices[j]
        mid = Point3D(
            (v1.x + v2.x) / 2.0,
            (v1.y + v2.y) / 2.0,
            (v1.z + v2.z) / 2.0
        )
        mid_idx = len(new_vertices)
        new_vertices.append(mid)
        edge_to_midpoint[edge] = mid_idx
        return mid_idx

    new_cells = []
    for tet in mesh.cells:
        v0, v1, v2, v3 = tet.v_indices

        # Midpoints of the 6 edges
        m01 = get_midpoint(v0, v1)
        m02 = get_midpoint(v0, v2)
        m03 = get_midpoint(v0, v3)
        m12 = get_midpoint(v1, v2)
        m13 = get_midpoint(v1, v3)
        m23 = get_midpoint(v2, v3)

        # 4 tetrahedra at the vertices
        new_cells.append((v0, m01, m02, m03))
        new_cells.append((v1, m01, m12, m13))
        new_cells.append((v2, m02, m12, m23))
        new_cells.append((v3, m03, m13, m23))

        # The remaining octahedron in the middle can be split into 4 tetrahedra
        # by choosing one of its diagonals. Let's use m01-m23 as the diagonal.
        new_cells.append((m01, m12, m02, m23))
        new_cells.append((m01, m12, m13, m23))
        new_cells.append((m01, m03, m13, m23))
        new_cells.append((m01, m02, m03, m23))

    return TetMesh(new_vertices, new_cells)


def refine_tetmesh_global(mesh: TetMesh) -> TetMesh:
    """
    Performs global refinement of the TetMesh using the midpoint split method.
    Each tetrahedron is subdivided into 8.
    """
    return refine_tetmesh_midpoint(mesh)

def refine_tetmesh_local(mesh: TetMesh, element_ids: List[int]) -> TetMesh:
    """
    Performs local refinement of the TetMesh on the specified elements.
    Uses centroid splitting to ensure the resulting mesh is conforming (no hanging nodes).
    """
    return refine_tetmesh_centroid(mesh, element_ids)

class TetMeshRefiner:
    """
    A class that provides various refinement algorithms for TetMesh.
    """
    def __init__(self, mesh: TetMesh):
        self.mesh = mesh

    def refine_centroid(self, element_ids: List[int] = None) -> TetMesh:
        """
        Refines the mesh by inserting a point at the centroid of each specified tetrahedron.
        """
        return refine_tetmesh_centroid(self.mesh, element_ids)

    def refine_midpoint(self) -> TetMesh:
        """
        Refines the mesh by splitting each edge at its midpoint.
        """
        return refine_tetmesh_midpoint(self.mesh)

    def refine_global(self) -> TetMesh:
        """
        Performs global refinement of the mesh.
        """
        return refine_tetmesh_global(self.mesh)

    def refine_local(self, element_ids: List[int]) -> TetMesh:
        """
        Performs local refinement of the mesh on specified elements.
        """
        return refine_tetmesh_local(self.mesh, element_ids)

    def refine_circumcenter(self, element_ids: List[int]) -> TetMesh:
        """
        Refines the mesh by inserting circumcenters of the specified tetrahedra.
        """
        from compgeom.mesh.volmesh.tetmesh.utils import get_tet_circumcenter
        new_vertices = list(self.mesh.vertices)
        new_cells = []
        
        ids_to_refine = set(element_ids)
        
        for i, tet in enumerate(self.mesh.cells):
            if i in ids_to_refine:
                v0, v1, v2, v3 = [self.mesh.vertices[idx] for idx in tet]
                cc, _ = get_tet_circumcenter(v0, v1, v2, v3)
                cc_idx = len(new_vertices)
                new_vertices.append(cc)
                
                # Split into 4 tets connecting circumcenter to each face
                new_cells.append((tet[0], tet[1], tet[2], cc_idx))
                new_cells.append((tet[0], tet[1], tet[3], cc_idx))
                new_cells.append((tet[0], tet[2], tet[3], cc_idx))
                new_cells.append((tet[1], tet[2], tet[3], cc_idx))
            else:
                new_cells.append(tet)
        
        return TetMesh(new_vertices, new_cells)

