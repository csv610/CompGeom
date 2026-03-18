from __future__ import annotations
import math
from collections import defaultdict
from typing import List, Optional, Tuple, Union

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshFace, MeshEdge

class TriMesh(Mesh):
    """A 2D or 3D mesh composed of triangular faces."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point2D, Point3D]], 
                 faces: List[Union[MeshFace, Tuple[int, ...]]], 
                 edges: Optional[List[MeshEdge]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        if faces and not isinstance(faces[0], MeshFace):
            faces = [MeshFace(i, f) for i, f in enumerate(faces)]
        super().__init__(nodes=nodes, faces=faces, edges=edges)

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Point2D, Point2D, Point2D]]) -> TriMesh:
        """Converts a list of Point triangles to a TriMesh object."""
        unique_points = []
        point_to_idx = {}
        
        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        nodes = [MeshNode(i, p) for i, p in enumerate(unique_points)]
        
        faces = []
        for i, tri in enumerate(triangles):
            v_indices = (point_to_idx[tri[0]], point_to_idx[tri[1]], point_to_idx[tri[2]])
            faces.append(MeshFace(i, v_indices))
            
        return cls(nodes, faces)

    @classmethod
    def from_file(cls, filename: str) -> TriMesh:
        """Creates a TriMesh from a file (OBJ, OFF, STL)."""
        from compgeom.mesh.surfmesh.meshio import MeshImporter
        mesh = MeshImporter.read(filename)
        
        nodes = mesh.nodes
        tri_faces = []
        face_id = 0
        for face in mesh.faces:
            v = face.v_indices
            if len(v) == 3:
                tri_faces.append(MeshFace(face_id, v))
                face_id += 1
            elif len(v) > 3:
                for i in range(1, len(v) - 1):
                    tri_faces.append(MeshFace(face_id, (v[0], v[i], v[i+1])))
                    face_id += 1
        return cls(nodes, tri_faces)

    def euler_characteristic(self) -> int:
        v = len(self.nodes)
        f = len(self.faces)
        edges = set()
        for face in self.faces:
            v_indices = face.v_indices
            edges.add(tuple(sorted((v_indices[0], v_indices[1]))))
            edges.add(tuple(sorted((v_indices[1], v_indices[2]))))
            edges.add(tuple(sorted((v_indices[2], v_indices[0]))))
        e = len(edges)
        return v - e + f

    def betti_numbers(self) -> tuple[int, int, int]:
        """
        Computes the Betti numbers (b0, b1, b2) of the triangle mesh.

        The mesh is treated as a 2-dimensional simplicial complex and the
        homology is computed over Z2. This avoids orientation requirements and
        works for open, closed, and disconnected triangle meshes.
        """
        vertex_count = len(self.nodes)

        edge_to_index: dict[tuple[int, int], int] = {}
        for face in self.faces:
            v_indices = face.v_indices
            for i in range(3):
                edge = tuple(sorted((v_indices[i], v_indices[(i + 1) % 3])))
                if edge not in edge_to_index:
                    edge_to_index[edge] = len(edge_to_index)

        edge_count = len(edge_to_index)
        face_count = len(self.faces)

        boundary_1_columns = [0] * edge_count
        for edge, edge_idx in edge_to_index.items():
            u, v = edge
            boundary_1_columns[edge_idx] = (1 << u) | (1 << v)

        boundary_2_columns = [0] * face_count
        for face_idx, face in enumerate(self.faces):
            column = 0
            v_indices = face.v_indices
            for i in range(3):
                edge = tuple(sorted((v_indices[i], v_indices[(i + 1) % 3])))
                column |= 1 << edge_to_index[edge]
            boundary_2_columns[face_idx] = column

        rank_boundary_1 = self._gf2_rank(boundary_1_columns)
        rank_boundary_2 = self._gf2_rank(boundary_2_columns)

        b0 = vertex_count - rank_boundary_1
        b1 = edge_count - rank_boundary_1 - rank_boundary_2
        b2 = face_count - rank_boundary_2
        return b0, b1, b2

    @staticmethod
    def _gf2_rank(columns: list[int]) -> int:
        """Returns the rank of a binary matrix given as integer bit-columns."""
        basis: dict[int, int] = {}
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

    def ensure_even_elements(self) -> TriMesh:
        """
        Ensures the mesh has an even number of triangles.
        If count is odd:
        1. Try to find a boundary edge and split it (adds 1 triangle).
        2. If no boundary exists, split one triangle into 4 (adds 3 triangles).
        """
        if len(self.faces) % 2 == 0:
            return self

        mesh = self._split_one_to_four(self)
        if len(mesh.faces) % 2 != 0:
            mesh = self._split_one_edge(mesh)
        return mesh

    @staticmethod
    def _split_one_to_four(mesh: TriMesh) -> TriMesh:
        def get_area(f_idx):
            face = mesh.faces[f_idx]
            v0, v1, v2 = [mesh.nodes[i].point for i in face.v_indices]
            ax, ay, az = v0.x, v0.y, getattr(v0, 'z', 0.0)
            bx, by, bz = v1.x, v1.y, getattr(v1, 'z', 0.0)
            cx, cy, cz = v2.x, v2.y, getattr(v2, 'z', 0.0)
            ux, uy, uz = bx - ax, by - ay, bz - az
            vx, vy, vz = cx - ax, cy - ay, cz - az
            cp_x, cp_y, cp_z = uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx
            return 0.5 * math.sqrt(cp_x**2 + cp_y**2 + cp_z**2)

        target_f_idx = max(range(len(mesh.faces)), key=get_area)
        target_face = mesh.faces[target_f_idx]
        target_v = target_face.v_indices
        
        edge_map = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            v = face.v_indices
            for j in range(3):
                edge = tuple(sorted((v[j], v[(j + 1) % 3])))
                edge_map[edge].append(i)
        
        new_nodes = list(mesh.nodes)
        mid_indices = []
        edges = []
        for j in range(3):
            u_idx, v_idx = target_v[j], target_v[(j + 1) % 3]
            edge = tuple(sorted((u_idx, v_idx)))
            edges.append(edge)
            
            mid_idx = len(new_nodes)
            v1_p, v2_p = mesh.nodes[u_idx].point, mesh.nodes[v_idx].point
            if isinstance(v1_p, Point3D) and isinstance(v2_p, Point3D):
                mid_p = Point3D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2, (v1_p.z+v2_p.z)/2)
            else:
                mid_p = Point2D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2)
            new_nodes.append(MeshNode(mid_idx, mid_p))
            mid_indices.append(mid_idx)
            
        m01, m12, m20 = mid_indices
        v0, v1, v2 = target_v
        
        new_face_tuples = []
        new_face_tuples.extend([(v0, m01, m20), (v1, m12, m01), (v2, m20, m12), (m01, m12, m20)])
        
        split_neighbor_indices = set()
        for j in range(3):
            edge = edges[j]
            mid = mid_indices[j]
            neighbors = [i for i in edge_map[edge] if i != target_f_idx]
            for n_idx in neighbors:
                split_neighbor_indices.add(n_idx)
                n_face = mesh.faces[n_idx]
                n_v = n_face.v_indices
                opposite = [v for v in n_v if v not in edge][0]
                new_face_tuples.append((edge[0], mid, opposite))
                new_face_tuples.append((edge[1], mid, opposite))
                
        final_face_tuples = list(new_face_tuples)
        for i, face in enumerate(mesh.faces):
            if i == target_f_idx or i in split_neighbor_indices:
                continue
            final_face_tuples.append(face.v_indices)
            
        final_faces = [MeshFace(i, v) for i, v in enumerate(final_face_tuples)]
        return TriMesh(new_nodes, final_faces)

    @staticmethod
    def _split_one_edge(mesh: TriMesh) -> TriMesh:
        edge_map = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            v = face.v_indices
            for j in range(3):
                edge = tuple(sorted((v[j], v[(j + 1) % 3])))
                edge_map[edge].append(i)
        
        boundary_edges = [e for e, faces in edge_map.items() if len(faces) == 1]
        
        if boundary_edges:
            edge = boundary_edges[0]
            f_idx = edge_map[edge][0]
            face = mesh.faces[f_idx]
            v_indices = face.v_indices
            new_nodes = list(mesh.nodes)
            mid_idx = len(new_nodes)
            v1_p, v2_p = mesh.nodes[edge[0]].point, mesh.nodes[edge[1]].point
            if isinstance(v1_p, Point3D) and isinstance(v2_p, Point3D):
                mid_p = Point3D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2, (v1_p.z+v2_p.z)/2)
            else:
                mid_p = Point2D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2)
            new_nodes.append(MeshNode(mid_idx, mid_p))
            opposite = [v for v in v_indices if v not in edge][0]
            new_face_tuples = [(edge[0], mid_idx, opposite), (edge[1], mid_idx, opposite)]
            final_face_tuples = [f.v_indices for i, f in enumerate(mesh.faces) if i != f_idx] + new_face_tuples
            final_faces = [MeshFace(i, v) for i, v in enumerate(final_face_tuples)]
            return TriMesh(new_nodes, final_faces)
        return mesh
