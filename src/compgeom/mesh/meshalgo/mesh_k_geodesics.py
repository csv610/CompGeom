"""K-Shortest geodesic paths calculations on surface meshes using Yen's Algorithm."""
import heapq
from typing import List, Tuple, Set, Dict

from compgeom.mesh import TriMesh
from mesh_geodesics import MeshGeodesics

class MeshKGeodesics:
    """Calculates multiple alternative shortest paths on a mesh."""

    @staticmethod
    def compute_k_shortest_paths(mesh: TriMesh, source_idx: int, target_idx: int, k: int) -> List[Tuple[float, List[int]]]:
        """
        Computes up to K shortest paths between source and target using Yen's algorithm.
        Returns a list of (distance, path) tuples.
        """
        if k <= 0:
            return []

        adj = MeshGeodesics.get_adjacency_list(mesh)
        
        # Initial shortest path
        dist, path = MeshKGeodesics._dijkstra_with_exclusions(mesh, source_idx, target_idx, adj)
        if not path:
            return []

        # A stores the K shortest paths
        A = [(dist, path)]
        # B stores potential candidate paths
        B = []

        for i in range(1, k):
            # The previous shortest path is the basis for deviations
            prev_path = A[-1][1]
            
            # Iterate through every node in the previous path as a deviation node
            for j in range(len(prev_path) - 1):
                deviation_node = prev_path[j]
                root_path = prev_path[:j + 1]

                excluded_edges = set()
                for _, p in A:
                    if p[:j + 1] == root_path:
                        excluded_edges.add(tuple(sorted((p[j], p[j+1]))))

                excluded_vertices = set(root_path[:-1])

                # Find the spur path from the deviation node to the target
                spur_dist, spur_path = MeshKGeodesics._dijkstra_with_exclusions(
                    mesh, deviation_node, target_idx, adj, excluded_edges, excluded_vertices
                )

                if spur_path:
                    total_path = root_path[:-1] + spur_path
                    # Calculate total distance
                    total_dist = 0.0
                    for m in range(len(total_path) - 1):
                        u, v = total_path[m], total_path[m+1]
                        # Find weight in adj
                        for neighbor, weight in adj[u]:
                            if neighbor == v:
                                total_dist += weight
                                break
                    
                    candidate = (total_dist, total_path)
                    if candidate not in B:
                        heapq.heappush(B, candidate)

            if not B:
                break

            # Move the best candidate to A
            next_best = heapq.heappop(B)
            # Ensure uniqueness in A
            while next_best in A and B:
                next_best = heapq.heappop(B)
            
            if next_best not in A:
                A.append(next_best)
            else:
                break

        return A

    @staticmethod
    def _dijkstra_with_exclusions(
        mesh: TriMesh, 
        source: int, 
        target: int, 
        adj: Dict[int, List[Tuple[int, float]]],
        excluded_edges: Set[Tuple[int, int]] = None,
        excluded_vertices: Set[int] = None
    ) -> Tuple[float, List[int]]:
        """
        Specialized Dijkstra implementation for Yen's algorithm.
        """
        num_vertices = len(mesh.vertices)
        distances = [float('inf')] * num_vertices
        predecessors = [None] * num_vertices
        distances[source] = 0.0
        
        pq = [(0.0, source)]
        
        while pq:
            d_curr, u = heapq.heappop(pq)
            
            if d_curr > distances[u]:
                continue
            
            if u == target:
                break
                
            if u not in adj:
                continue

            for v, weight in adj[u]:
                if excluded_vertices and v in excluded_vertices:
                    continue
                if excluded_edges and tuple(sorted((u, v))) in excluded_edges:
                    continue
                    
                new_dist = d_curr + weight
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    predecessors[v] = u
                    heapq.heappush(pq, (new_dist, v))
                    
        path = []
        if distances[target] == float('inf'):
            return float('inf'), path
            
        curr = target
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        return distances[target], path[::-1]
