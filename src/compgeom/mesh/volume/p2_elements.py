from __future__ import annotations
from typing import List, Tuple, Dict, Set
from compgeom.kernel import Point3D
from compgeom.mesh.mesh_base import MeshNode, MeshCell, MeshFace
from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh
from compgeom.mesh.surface.trimesh.trimesh import TriMesh

class P2Converter:
    """
    Converts linear elements (Tet4, Tri3) to quadratic elements (Tet10, Tri6).
    """
    @staticmethod
    def linear_to_quadratic_tet(mesh: TetMesh) -> Tuple[List[Point3D], List[Tuple[int, ...]]]:
        """
        Converts Tet4 to Tet10 by adding mid-edge nodes.
        Tet10 node ordering: 0-3 (vertices), 4-9 (mid-edges).
        Edges: (0,1), (1,2), (2,0), (0,3), (1,3), (2,3)
        """
        new_nodes = [n.point for n in mesh.nodes]
        edge_to_node = {}
        
        def get_mid_node(v1, v2):
            edge = tuple(sorted((v1, v2)))
            if edge not in edge_to_node:
                p1, p2 = new_nodes[v1], new_nodes[v2]
                mid_p = (p1 + p2) * 0.5
                edge_to_node[edge] = len(new_nodes)
                new_nodes.append(mid_p)
            return edge_to_node[edge]
            
        new_cells = []
        for cell in mesh.cells:
            v = cell.v_indices
            # 4 vertices
            v0, v1, v2, v3 = v[0], v[1], v[2], v[3]
            
            # 6 mid-edges
            m01 = get_mid_node(v0, v1)
            m12 = get_mid_node(v1, v2)
            m20 = get_mid_node(v2, v0)
            m03 = get_mid_node(v0, v3)
            m13 = get_mid_node(v1, v3)
            m23 = get_mid_node(v2, v3)
            
            new_cells.append((v0, v1, v2, v3, m01, m12, m20, m03, m13, m23))
            
        return new_nodes, new_cells

    @staticmethod
    def linear_to_quadratic_tri(mesh: TriMesh) -> Tuple[List[Point3D], List[Tuple[int, ...]]]:
        """
        Converts Tri3 to Tri6.
        Tri6 node ordering: 0-2 (vertices), 3-5 (mid-edges).
        Edges: (0,1), (1,2), (2,0)
        """
        new_nodes = [n.point for n in mesh.nodes]
        edge_to_node = {}
        
        def get_mid_node(v1, v2):
            edge = tuple(sorted((v1, v2)))
            if edge not in edge_to_node:
                p1, p2 = new_nodes[v1], new_nodes[v2]
                mid_p = (p1 + p2) * 0.5
                edge_to_node[edge] = len(new_nodes)
                new_nodes.append(mid_p)
            return edge_to_node[edge]
            
        new_faces = []
        for face in mesh.faces:
            v = face.v_indices
            v0, v1, v2 = v[0], v[1], v[2]
            
            m01 = get_mid_node(v0, v1)
            m12 = get_mid_node(v1, v2)
            m20 = get_mid_node(v2, v0)
            
            new_faces.append((v0, v1, v2, m01, m12, m20))
            
        return new_nodes, new_faces
