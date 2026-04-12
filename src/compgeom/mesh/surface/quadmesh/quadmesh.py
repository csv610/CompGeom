from __future__ import annotations
from typing import List, Optional, Tuple, Union, Any, Set

from compgeom.mesh.mesh_base import MeshNode, MeshFace, MeshEdge
from compgeom.mesh.mesh_topology import MeshTopology
from compgeom.mesh.surface.surface_mesh import SurfaceMesh


class QuadMesh(SurfaceMesh):
    """A 2D or 3D mesh composed of quadrilateral faces."""

    def __init__(
        self,
        nodes: List[Union[MeshNode, Any]],
        faces: List[Union[MeshFace, Tuple[int, ...]]],
        edges: Optional[List[MeshEdge]] = None,
    ):
        super().__init__(nodes=nodes, faces=faces, edges=edges)

    @classmethod
    def create_structured_mesh(
        cls, nx: int, ny: int, origin_x: float = 0.0, origin_y: float = 0.0, spacing: float = 1.0
    ) -> "QuadMesh":
        """Creates a 2D structured quad grid.

        Args:
            nx: Number of cells in X direction.
            ny: Number of cells in Y direction.
            origin_x: Origin X coordinate.
            origin_y: Origin Y coordinate.
            spacing: Cell spacing.

        Returns:
            A new QuadMesh with structured quad faces.
        """
        from compgeom.kernel import Point3D

        vertices = []
        for j in range(ny):
            for i in range(nx):
                vertices.append(Point3D(origin_x + i * spacing, origin_y + j * spacing, 0.0))

        faces = []
        for j in range(ny - 1):
            for i in range(nx - 1):
                v0 = j * nx + i
                v1 = j * nx + (i + 1)
                v2 = (j + 1) * nx + (i + 1)
                v3 = (j + 1) * nx + i
                faces.append((v0, v1, v2, v3))

        return cls(nodes=vertices, faces=faces)

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Any, Any, Any]]) -> "QuadMesh":
        """Converts a list of Point triangles to a QuadMesh object."""
        unique_points = []
        point_to_idx = {}

        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)

        nodes = [MeshNode(i, p) for i, p in enumerate(unique_points)]
        faces = [
            MeshFace(i, (point_to_idx[t[0]], point_to_idx[t[1]], point_to_idx[t[2]])) for i, t in enumerate(triangles)
        ]

        return cls(nodes, faces)

    @classmethod
    def from_file(cls, filename: str) -> QuadMesh:
        """Creates a QuadMesh from a file (OBJ, OFF, STL)."""
        from compgeom.mesh import from_file as read_mesh

        mesh = read_mesh(filename)
        return cls(mesh.nodes, mesh.faces)

    def extract_chord(self, start_quad_idx: int, edge_index: int) -> List[int]:
        """
        Extracts a topological chord starting from a given quad and its edge.
        A chord is a sequence of topologically parallel edges across adjacent quads.

        Extraction starts in both directions from the starting quad to ensure
        completeness, especially if one side ends at a boundary.

        Traversal stops if:
        1. A boundary edge is reached.
        2. The traversal returns to the starting quad and edge (closed loop).

        Args:
            start_quad_idx: Index of the starting quadrilateral.
            edge_index: Which edge of the quad to start from (0, 1, 2, or 3).
                        Parallel edge is (edge_index + 2) % 4.

        Returns:
            A list of quadrilateral indices forming the chord.
        """
        if start_quad_idx < 0 or start_quad_idx >= len(self.faces):
            raise ValueError("Invalid quad index.")

        # Direction A: Forward extraction starting by crossing edge_index
        # We simulate entry from the opposite side
        path_forward, loop_f = self._traverse_chord_v2(start_quad_idx, (edge_index + 2) % 4, set())

        if loop_f:
            # If closed loop, the forward path already covers the cycle
            return [start_quad_idx] + path_forward

        # Direction B: Backward extraction starting by crossing opposite_edge_index
        # We simulate entry from edge_index
        path_backward, _ = self._traverse_chord_v2(start_quad_idx, edge_index, set(path_forward) | {start_quad_idx})

        # Assemble: reversed(backward) + start + forward
        return list(reversed(path_backward)) + [start_quad_idx] + path_forward

    def _traverse_chord_v2(
        self, start_idx: int, entry_edge_idx: int, global_visited: Set[int]
    ) -> Tuple[List[int], bool]:
        path = []
        # State: (quad_idx, entry_edge_idx)
        visited_states = set()

        curr_idx = start_idx
        curr_entry = entry_edge_idx

        while True:
            # Exit from opposite side
            exit_edge_idx = (curr_entry + 2) % 4
            curr_face = self.faces[curr_idx]
            v_indices = curr_face.v_indices
            u, v = v_indices[exit_edge_idx], v_indices[(exit_edge_idx + 1) % 4]
            exit_edge = tuple(sorted((u, v)))

            # Find neighbor across exit_edge
            next_idx = None
            next_entry = -1

            for n_idx in MeshTopology(self).shared_edge_neighbors(curr_idx):
                n_face = self.faces[n_idx]
                n_v = n_face.v_indices
                n_edges = [tuple(sorted((n_v[k], n_v[(k + 1) % 4]))) for k in range(4)]
                if exit_edge in n_edges:
                    next_idx = n_idx
                    next_entry = n_edges.index(exit_edge)
                    break

            if next_idx is None:
                # Boundary reached (no neighbor sharing the exit edge)
                return path, False

            if next_idx == start_idx:
                # Returned to starting element
                return path, True

            if next_idx in global_visited or (next_idx, next_entry) in visited_states:
                # Collision with other part of the chord
                return path, False

            path.append(next_idx)
            visited_states.add((next_idx, next_entry))
            curr_idx = next_idx
            curr_entry = next_entry
