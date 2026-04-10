"""Matroid Theory for Mesh Analysis.

Implements matroid structures for use in mesh topology,
including graphic matroids, circuit computation,
and basis exchange algorithms.

References:
    - Oxley, "Matroid Theory", 1992
    - Whitney, "On the Abstract Properties of Linear Dependence", 1935
    - Tutte, "Introduction to Matroid Theory", 1965
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, FrozenSet

import numpy as np


class Matroid:
    r"""Abstract matroid base class.

    A matroid M = (E, I) consists of:
    - E: ground set of elements
    - I: independent subsets of E

    Satisfying:
    1. Hereditary: if B ∈ I and A ⊆ B, then A ∈ I
    2. Exchange: if A, B ∈ I and |A| < |B|, then ∃e ∈ B\A where A∪{e} ∈ I
    """

    def __init__(self, ground_set: Set) -> None:
        self.E = ground_set
        self._rank_cache: Dict[frozenset, int] = {}

    def rank(self, subset: Set) -> int:
        """Compute rank of a subset."""
        raise NotImplementedError

    def is_independent(self, subset: Set) -> bool:
        """Check if subset is independent."""
        return self.rank(subset) == len(subset)

    def bases(self) -> List[Set]:
        """Find all bases (maximal independent sets)."""
        raise NotImplementedError

    def circuits(self) -> List[Set]:
        """Find all circuits (minimal dependent sets)."""
        raise NotImplementedError


class GraphicMatroid(Matroid):
    """Graphic matroid from a graph/mesh.

    The graphic matroid M(G) has:
    - E: edges of the graph
    - I: forests (acyclic edge sets)

    A set of edges is independent iff it contains no cycles.
    """

    def __init__(self, edges: List[tuple], num_vertices: int) -> None:
        self.edges = edges
        self.num_vertices = num_vertices
        ground_set = set(range(len(edges)))
        super().__init__(ground_set)

        self._adj: Dict[int, List[int]] = self._build_adjacency()
        self._components_cache: Dict[frozenset, int] = {}

    def _build_adjacency(self) -> Dict[int, List[int]]:
        adj: Dict[int, List[int]] = {i: [] for i in range(len(self.edges))}
        for ei, (u, v) in enumerate(self.edges):
            adj[ei].extend([u, v])
        return adj

    def rank(self, edge_set: Set) -> int:
        """Rank of edge set = |V| - components(edge set)."""
        if not edge_set:
            return 0

        key = frozenset(edge_set)
        if key in self._rank_cache:
            return self._rank_cache[key]

        parent = list(range(self.num_vertices))

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
                return True
            return False

        for ei in edge_set:
            u, v = self.edges[ei]
            union(u, v)

        components = len(set(find(i) for i in range(self.num_vertices) if any(i in self.edges[ei] for ei in edge_set)))

        rank = self.num_vertices - components
        self._rank_cache[key] = rank
        return rank

    def is_independent(self, edge_set: Set) -> bool:
        """Edge set is independent iff it's a forest."""
        return self.rank(edge_set) == len(edge_set)

    def is_dependent(self, edge_set: Set) -> bool:
        """Edge set contains a cycle."""
        return not self.is_independent(edge_set)

    def find_circuit(self, edge_subset: Set, added_edge: int) -> Set:
        """Find the unique circuit when added_edge is added to edge_subset.

        Uses the fundamental cycle: path in the forest from added_edge's
        endpoints, plus the added edge.
        """
        u, v = self.edges[added_edge]

        parent = list(range(self.num_vertices))

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
                return True
            return False

        for ei in edge_subset:
            eu, ev = self.edges[ei]
            union(eu, ev)

        if find(u) != find(v):
            return set()

        path_edges = set()
        visited = set()

        def dfs(start, target, current_path):
            if start == target:
                return True
            visited.add(start)
            for ei in edge_subset:
                eu, ev = self.edges[ei]
                if start in (eu, ev):
                    next_v = ev if eu == start else eu
                    if next_v not in visited:
                        new_path = current_path | {ei}
                        if dfs(next_v, target, new_path):
                            return True
            return False

        dfs(u, v, set())

        return {added_edge} | path_edges

    def bases(self) -> List[Set]:
        """Generate all bases (spanning forests with |V|-1 edges)."""
        from itertools import combinations

        target_rank = self.num_vertices - 1
        bases = []

        for k in range(target_rank, len(self.edges) + 1):
            for combo in combinations(range(len(self.edges)), k):
                edge_set = set(combo)
                if self.rank(edge_set) == target_rank:
                    bases.append(edge_set)

            if bases:
                break

        return bases

    def circuits(self) -> List[Set]:
        """Find all fundamental circuits."""
        from itertools import combinations

        circuits = []
        n = self.num_vertices

        for combo in combinations(range(len(self.edges)), n):
            edge_set = set(combo)
            if self.is_dependent(edge_set):
                for ei in edge_set:
                    circuit = self.find_circuit(edge_set - {ei}, ei)
                    if circuit and circuit not in circuits:
                        circuits.append(circuit)

        return circuits

    def fundamental_circuits(self, edge_set: Set) -> Dict[int, Set]:
        """Find fundamental circuits for each edge in edge_set."""
        result = {}
        for ei in edge_set:
            other = edge_set - {ei}
            if self.is_dependent(edge_set):
                circuit = self.find_circuit(other, ei)
                result[ei] = circuit
        return result


class TransversalMatroid(Matroid):
    """Transversal matroid from bipartite matching.

    M has ground set = left vertices
    Independent sets = those with matching in the bipartite graph.
    """

    def __init__(self, left_vertices: Set, right_vertices: Set, edges: List[tuple]) -> None:
        self.L = left_vertices
        self.R = right_vertices
        self.bipartite_edges = edges
        super().__init__(left_vertices)

    def rank(self, subset: Set) -> int:
        """Size of maximum matching reachable from subset."""
        from scipy.optimize import linear_sum_assignment

        left_to_right: Dict[int, List[int]] = {v: [] for v in self.L}
        for l, r in self.bipartite_edges:
            if l in subset:
                left_to_right[l].append(r)

        n = len(self.L)
        cost_matrix = np.full((n, n), 1000)
        for i, l in enumerate(self.L):
            for j, r in enumerate(self.R):
                if r in left_to_right[l]:
                    cost_matrix[i, j] = 0

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        matching_size = sum(1 for i, j in zip(row_ind, col_ind) if cost_matrix[i, j] == 0)

        return matching_size


def matroid_union(matroid1: Matroid, matroid2: Matroid) -> Matroid:
    """Compute union of two matroids."""
    raise NotImplementedError


def matroid_intersection(matroid1: Matroid, matroid2: Matroid) -> Matroid:
    """Compute intersection of two matroids."""
    raise NotImplementedError


class MeshGraphicMatroid(GraphicMatroid):
    """Graphic matroid specialized for triangle meshes.

    Uses mesh edges as ground set, forests as independent sets.
    Useful for computing cuts, cycles, and topology.
    """

    def __init__(self, mesh) -> None:
        edges: List[tuple] = []

        for face in mesh.faces:
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                if edge not in [e[1] for e in edges]:
                    edges.append((len(mesh.nodes), edge[0], edge[1]))

        num_v = len(mesh.nodes)
        edge_tuples = [(e[1], e[2]) for e in edges]

        super().__init__(edge_tuples, num_v)

    def find_cut_edges(self) -> Set[int]:
        """Find edges whose removal disconnects the mesh."""
        cut_edges = set()

        for ei in range(len(self.edges)):
            test_set = set(range(len(self.edges))) - {ei}
            if self.rank(test_set) < self.num_vertices - 1:
                cut_edges.add(ei)

        return cut_edges

    def find_cycle_edges(self) -> Set[int]:
        """Find edges that belong to cycles."""
        cycle_edges = set()

        full_rank = self.rank(set(range(len(self.edges))))

        for ei in range(len(self.edges)):
            test_set = set(range(len(self.edges))) - {ei}
            if self.rank(test_set) == full_rank:
                cycle_edges.add(ei)

        return cycle_edges


def create_graphic_matroid(mesh) -> MeshGraphicMatroid:
    """Create graphic matroid from mesh.

    Args:
        mesh: TriMesh with nodes and faces

    Returns:
        MeshGraphicMatroid instance
    """
    return MeshGraphicMatroid(mesh)
