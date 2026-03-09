"""Algorithms for decomposing polygons into convex pieces."""

from __future__ import annotations

from typing import List, Set, Tuple

from ..geometry import Point, cross_product
from .polygon import get_triangulation_with_diagonals, _ensure_ccw


class ConvexDecomposer:
    """Decomposes simple polygons into convex parts."""

    @staticmethod
    def hertel_mehlhorn(polygon: List[Point]) -> List[List[Point]]:
        """
        Decomposes a simple polygon into convex pieces using the Hertel-Mehlhorn algorithm.
        
        Args:
            polygon: List of points defining a simple polygon.
            
        Returns:
            A list of polygons, where each polygon is a list of Points.
        """
        if len(polygon) < 3:
            return [polygon]

        # 1. Triangulate and get diagonals
        tri_indices, diagonals, vertices = get_triangulation_with_diagonals(polygon)
        
        # 2. Represent partitions as sets of vertex indices
        # Start with triangles
        partitions: List[Set[int]] = [set(t) for f in tri_indices for t in [f]] # tri_indices is already a list of tuples
        
        # Adjust partitions initialization if tri_indices format is different
        # In polygon.py: triangles.append(tuple(working_indices))
        # So tri_indices is List[Tuple[int, int, int]]
        partitions = [set(t) for t in tri_indices]

        # 3. Identify reflex vertices (indices)
        n = len(vertices)
        reflex_indices = set()
        for i in range(n):
            if cross_product(vertices[i - 1], vertices[i], vertices[(i + 1) % n]) <= 0:
                reflex_indices.add(i)

        # 4. Try to remove each diagonal
        for diag in diagonals:
            u, v = diag
            
            # A diagonal can be removed if it doesn't create a reflex vertex in the merged partition
            # A diagonal uv is essential if u or v is a reflex vertex in the ORIGINAL polygon
            # AND removing it would leave that vertex reflex in the new partition.
            # Simplified HM: If neither endpoint is a reflex vertex of the original polygon,
            # the diagonal is definitely non-essential.
            if u not in reflex_indices and v not in reflex_indices:
                # Find the two partitions sharing this diagonal
                p_indices = [i for i, p in enumerate(partitions) if u in p and v in p]
                
                if len(p_indices) == 2:
                    idx1, idx2 = p_indices
                    # Merge them
                    merged = partitions[idx1] | partitions[idx2]
                    partitions.pop(max(idx1, idx2))
                    partitions.pop(min(idx1, idx2))
                    partitions.append(merged)

        # 5. Convert index sets back to ordered lists of Points
        result = []
        for p_set in partitions:
            # Sort indices according to original polygon order to keep them consistent
            ordered_indices = sorted(list(p_set))
            # However, simple sorting might not work for non-convex if we just pick vertices.
            # But since the pieces ARE convex and their vertices are a subset of the original,
            # sorting by original index (in a CCW polygon) will give them in CCW order.
            result.append([vertices[i] for i in ordered_indices])
            
        return result


__all__ = ["ConvexDecomposer"]
