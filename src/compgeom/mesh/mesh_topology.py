"""Topological queries for meshes."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING, Any

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh_base import Mesh, MeshFace, MeshEdge

if TYPE_CHECKING:
    from compgeom.mesh.mesh_base import Mesh


def mesh_neighbors(triangles: list[tuple[Any, ...]]) -> dict:
    """
    Computes neighbor relationships for a list of triangles.
    Returns a dict with 'vertex_neighbors' and 'triangle_neighbors'.
    """
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh

    # 1. Flatten triangles into unique vertices and faces
    unique_points = []
    point_to_id = {}
    faces = []

    for tri in triangles:
        tri_face = []
        for p in tri:
            # Use id if available, otherwise coordinates
            p_id = getattr(p, "id", -1)
            if p_id != -1 and p_id in point_to_id:
                tri_face.append(point_to_id[p_id])
            else:
                p_key = (p.x, p.y, getattr(p, "z", 0.0))
                if p_key not in point_to_id:
                    point_to_id[p_key] = len(unique_points)
                    if p_id != -1:
                        point_to_id[p_id] = point_to_id[p_key]
                    unique_points.append(p)
                tri_face.append(point_to_id[p_key])
        faces.append(tuple(tri_face))

    # 2. Build temporary TriMesh to use MeshTopology
    mesh = TriMesh(unique_points, faces)
    topo = MeshTopology(mesh)

    # 3. Extract neighbors
    v_neighbors = {}
    for i in range(len(unique_points)):
        v_neighbors[i] = list(topo.vertex_neighbors(i))

    t_neighbors = {}
    for i in range(len(faces)):
        t_neighbors[i] = list(topo.element_neighbors(i))

    return {"vertex_neighbors": v_neighbors, "triangle_neighbors": t_neighbors}


def get_mesh_edges(triangles: list[tuple[Any, ...]]) -> set[tuple[int, int]]:
    """Extracts unique vertex id pairs from a list of triangles."""
    edges = set()
    for tri in triangles:
        n = len(tri)
        for i in range(n):
            u, v = getattr(tri[i], "id", i), getattr(tri[(i + 1) % n], "id", (i + 1) % n)
            edges.add(tuple(sorted((u, v))))
    return edges


class MeshTopology:
    """Provides topological queries for a mesh."""

    def __init__(self, mesh: Mesh):
        self._mesh = mesh
        self._v2v: Optional[Dict[int, Set[int]]] = None
        self._v2e: Optional[Dict[int, Set[int]]] = None
        self._e2e: Optional[Dict[int, Set[int]]] = None
        self._e2e_edge: Optional[Dict[int, Set[int]]] = None

    @staticmethod
    def extract_edges(faces: List[MeshFace]) -> List[MeshEdge]:
        """Extracts unique edges from faces."""
        from compgeom.mesh.mesh_base import MeshEdge

        edge_set: Set[Tuple[int, int]] = set()
        edges = []
        edge_id = 0
        for face in faces:
            v = face.v_indices
            n = len(v)
            for i in range(n):
                a, b = v[i], v[(i + 1) % n]
                key = (min(a, b), max(a, b))
                if key not in edge_set:
                    edge_set.add(key)
                    edges.append(MeshEdge(edge_id, key))
                    edge_id += 1
        return edges

    @staticmethod
    def extract_faces(cells: List) -> List[MeshFace]:
        """Extracts unique faces from cells (for volume mesh)."""
        from compgeom.mesh.mesh_base import MeshFace

        face_set: Set[Tuple[int, ...]] = set()
        faces = []
        face_id = 0

        def canonical_face(face_v: Tuple[int, ...]) -> Tuple[int, ...]:
            return tuple(sorted(face_v))

        for cell in cells:
            v = cell.v_indices
            n = len(v)
            if n == 4:
                face_indices = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
            elif n == 8:
                face_indices = [
                    (0, 1, 2, 3),
                    (0, 1, 4, 5),
                    (0, 2, 4, 6),
                    (1, 3, 5, 7),
                    (2, 3, 6, 7),
                    (4, 5, 6, 7),
                ]
            else:
                continue

            for idx in face_indices:
                face_v = tuple(v[i] for i in idx)
                key = canonical_face(face_v)
                if key not in face_set:
                    face_set.add(key)
                    faces.append(MeshFace(face_id, key))
                    face_id += 1

        return faces

    def vertex_neighbors(self, vertex_idx: int) -> Set[int]:
        """Returns the set of vertex indices adjacent to the given vertex."""
        if self._v2v is None:
            self._build_v2v()
        return self._v2v.get(vertex_idx, set())

    def vertex_elements(self, vertex_idx: int) -> Set[int]:
        """Returns the set of element indices sharing the given vertex."""
        if self._v2e is None:
            self._build_v2e()
        return self._v2e.get(vertex_idx, set())

    def element_neighbors(self, element_idx: int) -> Set[int]:
        """Returns the set of element indices sharing at least one vertex."""
        if self._e2e is None:
            self._build_e2e()
        return self._e2e.get(element_idx, set())

    def shared_edge_neighbors(self, element_idx: int) -> Set[int]:
        """Returns the set of element indices sharing an edge (at least 2 vertices)."""
        if self._e2e_edge is None:
            self._build_e2e_edge()
        return self._e2e_edge.get(element_idx, set())

    def is_watertight(self) -> bool:
        """Returns True if the mesh is closed."""
        if self._mesh.cells:
            return len(self.boundary_faces()) == 0
        return len(self.boundary_edges()) == 0

    def get_edges(self) -> Set[Tuple[int, int]]:
        """Extracts unique sorted edges from the mesh topology."""
        edges = set()
        n_vertices = len(self._mesh.vertices)
        for i in range(n_vertices):
            for neighbor in self.vertex_neighbors(i):
                if i < neighbor:
                    edges.add((i, neighbor))
        return edges

    def boundary_edges(self) -> List[Tuple[int, int]]:
        """Returns a list of edges (as vertex index pairs) that belong to only one element."""
        edge_count = defaultdict(int)

        elements = (
            [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        )
        for element in elements:
            for edge in self._get_element_edges(element):
                sorted_edge = tuple(sorted(edge))
                edge_count[sorted_edge] += 1

        return [edge for edge, count in edge_count.items() if count == 1]

    def boundary_loops(self) -> List[List[int]]:
        """Extracts boundary loops from the mesh."""
        b_edges = self.boundary_edges()
        if not b_edges:
            return []

        adj = defaultdict(list)
        for u, v in b_edges:
            adj[u].append(v)
            adj[v].append(u)

        loops = []
        visited = set()
        for start_node in list(adj.keys()):
            if start_node in visited:
                continue

            loop = []
            curr = start_node
            prev = -1
            while curr is not None and curr not in visited:
                visited.add(curr)
                loop.append(curr)
                next_nodes = adj[curr]
                next_node = None
                for n in next_nodes:
                    if n != prev:
                        next_node = n
                        break
                prev = curr
                curr = next_node
                if curr == start_node:
                    break
            if loop:
                loops.append(loop)
        return loops

    def _get_element_edges(self, v_indices: Tuple[int, ...]) -> List[Tuple[int, int]]:
        """Internal helper to decompose an element into its constituent edges."""
        n = len(v_indices)
        if self._mesh.cells and n == 4:
            v = v_indices
            return [(v[0], v[1]), (v[0], v[2]), (v[0], v[3]), (v[1], v[2]), (v[1], v[3]), (v[2], v[3])]
        elif self._mesh.cells and n == 8:
            v = v_indices
            return [
                (v[0], v[1]), (v[1], v[2]), (v[2], v[3]), (v[3], v[0]),
                (v[4], v[5]), (v[5], v[6]), (v[6], v[7]), (v[7], v[4]),
                (v[0], v[4]), (v[1], v[5]), (v[2], v[6]), (v[3], v[7]),
            ]
        return [(v_indices[i], v_indices[(i + 1) % n]) for i in range(n)]

    def boundary_faces(self) -> List[Tuple[int, ...]]:
        """Returns boundary faces."""
        if not self._mesh.cells:
            return []
        face_count = defaultdict(int)
        for cell in self._mesh.cells:
            for face in self._get_cell_faces(cell):
                canonical_face = tuple(sorted(face))
                face_count[canonical_face] += 1
        return [face for face, count in face_count.items() if count == 1]

    def _get_cell_faces(self, cell: Any) -> List[Tuple[int, ...]]:
        v = cell.v_indices
        n = len(v)
        if n == 4:
            return [(v[0], v[1], v[2]), (v[0], v[1], v[3]), (v[0], v[2], v[3]), (v[1], v[2], v[3])]
        elif n == 8:
            return [
                (v[0], v[3], v[2], v[1]), (v[4], v[5], v[6], v[7]),
                (v[0], v[1], v[5], v[4]), (v[1], v[2], v[6], v[5]),
                (v[2], v[3], v[7], v[6]), (v[3], v[0], v[4], v[7]),
            ]
        return [v]

    def euler_characteristic(self) -> int:
        """Computes the Euler characteristic (V - E + F)."""
        v = len(self._mesh.vertices)
        e = len(self.get_edges())
        f = len(self._mesh.faces)
        return v - e + f

    def genus(self) -> float:
        """Computes the genus of the surface."""
        chi = self.euler_characteristic()
        b = len(self.boundary_loops())
        # For orientable surface: chi = 2 - 2g - b => 2g = 2 - chi - b
        return (2 - chi - b) / 2.0

    def is_orientable(self) -> bool:
        """Checks if the mesh is orientable."""
        if not self._mesh.faces:
            return True
            
        # BFS to check for consistent orientation
        edge_to_face = defaultdict(list)
        for i, face in enumerate(self._mesh.faces):
            v = face.v_indices
            for j in range(len(v)):
                edge = tuple(sorted((v[j], v[(j + 1) % len(v)])))
                edge_to_face[edge].append(i)
                
        visited = [False] * len(self._mesh.faces)
        face_orientation = [1] * len(self._mesh.faces) # 1 for original, -1 for flipped
        
        for start_face in range(len(self._mesh.faces)):
            if visited[start_face]:
                continue
                
            queue = deque([start_face])
            visited[start_face] = True
            
            while queue:
                curr_idx = queue.popleft()
                curr_face = self._mesh.faces[curr_idx].v_indices
                curr_orient = face_orientation[curr_idx]
                
                for j in range(len(curr_face)):
                    u, v = curr_face[j], curr_face[(j + 1) % len(curr_face)]
                    edge = tuple(sorted((u, v)))
                    
                    for neighbor_idx in edge_to_face[edge]:
                        if neighbor_idx == curr_idx:
                            continue
                            
                        neighbor_face = self._mesh.faces[neighbor_idx].v_indices
                        # Find the edge in neighbor_face
                        for k in range(len(neighbor_face)):
                            nu, nv = neighbor_face[k], neighbor_face[(k + 1) % len(neighbor_face)]
                            if (nu == u and nv == v) or (nu == v and nv == u):
                                # Consistent orientation means edges are traversed in opposite directions
                                # If we travel u->v in curr, we should travel v->u in neighbor
                                expected_nv = u if nu == v else v # this is always true if they match
                                
                                # If u->v in curr, then nu must be v and nv must be u for consistent orientation
                                is_reversed = (nu == v and nv == u)
                                
                                if not visited[neighbor_idx]:
                                    visited[neighbor_idx] = True
                                    face_orientation[neighbor_idx] = curr_orient if is_reversed else -curr_orient
                                    queue.append(neighbor_idx)
                                else:
                                    # Already visited, check if orientation is consistent
                                    actual_orient = face_orientation[neighbor_idx]
                                    required_orient = curr_orient if is_reversed else -curr_orient
                                    if actual_orient != required_orient:
                                        return False
        return True

    def is_oriented(self) -> bool:
        """Checks if the mesh is consistently oriented."""
        if not self._mesh.faces:
            return True
            
        edge_usage = defaultdict(int)
        for face in self._mesh.faces:
            v = face.v_indices
            for j in range(len(v)):
                edge = (v[j], v[(j + 1) % len(v)])
                edge_usage[edge] += 1
                
        for edge, count in edge_usage.items():
            rev_edge = (edge[1], edge[0])
            if count > 1: # Self-intersecting orientation?
                return False
            # For manifold mesh, each edge (u,v) should have at most one face using it
            # and its reverse (v,u) should be used by the neighbor face.
            # If (u,v) is used twice, it's definitely not consistently oriented.
        return True

    def _build_v2v(self):
        self._v2v = defaultdict(set)
        elements = (
            [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        )
        for element in elements:
            for u, v in self._get_element_edges(element):
                self._v2v[u].add(v)
                self._v2v[v].add(u)

    def _build_v2e(self):
        self._v2e = defaultdict(set)
        elements = (
            [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        )
        for i, element in enumerate(elements):
            for v_idx in element:
                self._v2e[v_idx].add(i)

    def _build_e2e(self):
        if self._v2e is None:
            self._build_v2e()
        self._e2e = defaultdict(set)
        elements = (
            [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        )
        for i, element in enumerate(elements):
            for v_idx in element:
                for neighbor_idx in self._v2e[v_idx]:
                    if neighbor_idx != i:
                        self._e2e[i].add(neighbor_idx)

    def _build_e2e_edge(self):
        self._e2e_edge = defaultdict(set)
        edge_map = defaultdict(list)
        elements = (
            [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        )
        for i, element in enumerate(elements):
            for edge in self._get_element_edges(element):
                sorted_edge = tuple(sorted(edge))
                edge_map[sorted_edge].append(i)
        for sharing_elements in edge_map.values():
            if len(sharing_elements) > 1:
                for i in range(len(sharing_elements)):
                    for j in range(i + 1, len(sharing_elements)):
                        u, v = sharing_elements[i], sharing_elements[j]
                        self._e2e_edge[u].add(v)
                        self._e2e_edge[v].add(u)


__all__ = ["MeshTopology", "mesh_neighbors"]
