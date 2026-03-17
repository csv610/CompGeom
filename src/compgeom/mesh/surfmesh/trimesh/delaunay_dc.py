"""Divide and Conquer Delaunay Triangulation."""

from __future__ import annotations
import math
from ....kernel import Point2D, orientation_sign, in_circle, segment_angle as angle


def triangulate_divide_and_conquer(points: list[Point2D]) -> list[tuple[Point2D, Point2D, Point2D]]:
    """Delaunay Triangulation using the Divide and Conquer algorithm."""
    mesher = DivideAndConquerDelaunayMesher()
    return mesher.triangulate(points)


class DivideAndConquerDelaunayMesher:
    """
    Delaunay Triangulation Mesher using the Divide and Conquer algorithm.
    """
    def __init__(self):
        self.points: list[Point2D] = []

    def triangulate(self, points: list[Point2D]) -> list[tuple[Point2D, Point2D, Point2D]]:
        """
        Performs Delaunay triangulation of the given points.
        
        Returns:
            A list of triangles.
        """
        if not points:
            return []
        
        # Sort points and remove duplicates
        sorted_points = sorted(points, key=lambda p: (p.x, p.y))
        unique_points = []
        for p in sorted_points:
            if unique_points and p.x == unique_points[-1].x and p.y == unique_points[-1].y:
                continue
            unique_points.append(p)
        
        if len(unique_points) < 2:
            return []

        self.points = unique_points
        adj = self._dc_triangulate(unique_points)
        
        # Convert adjacency list to unique triangles
        triangles = []
        seen = set()
        for u in unique_points:
            if u not in adj: continue
            for v in adj[u]:
                if v not in adj: continue
                for w in adj[v]:
                    if w not in adj: continue
                    if w in adj[u]:
                        tri_key = tuple(sorted((u.id, v.id, w.id)))
                        if tri_key not in seen:
                            # Ensure CCW orientation for consistency
                            if orientation_sign(u, v, w) > 0:
                                triangles.append((u, v, w))
                            elif orientation_sign(u, v, w) < 0:
                                triangles.append((u, w, v))
                            seen.add(tri_key)
        
        return triangles

    def _dc_triangulate(self, points: list[Point2D]) -> dict[Point2D, list[Point2D]]:
        n = len(points)
        if n <= 3:
            adj = {p: [] for p in points}
            if n == 2:
                u, v = points
                adj[u].append(v)
                adj[v].append(u)
            elif n == 3:
                u, v, w = points
                orient = orientation_sign(u, v, w)
                if orient == 0:
                    # Collinear: connect consecutive points only
                    adj[u].append(v)
                    adj[v].extend([u, w])
                    adj[w].append(v)
                else:
                    adj[u].extend([v, w])
                    adj[v].extend([u, w])
                    adj[w].extend([u, v])
            for p in adj:
                adj[p].sort(key=lambda neighbor: angle(p, neighbor))
            return adj

        mid = n // 2
        left_adj = self._dc_triangulate(points[:mid])
        right_adj = self._dc_triangulate(points[mid:])
        
        # Combined adjacency dictionary
        adj = {**left_adj, **right_adj}

        # 1. Find the base LR edge (lowest common tangent)
        ld = points[mid - 1]
        rd = points[mid]
        
        while True:
            changed = False
            for neighbor in adj[ld]:
                if orientation_sign(rd, ld, neighbor) < 0:
                    ld = neighbor
                    changed = True
                    break
            if changed: continue
            
            for neighbor in adj[rd]:
                if orientation_sign(ld, rd, neighbor) > 0:
                    rd = neighbor
                    changed = True
                    break
            if not changed:
                break

        # 2. Merge step: move up from the base edge
        while True:
            if rd not in adj[ld]: adj[ld].append(rd)
            if ld not in adj[rd]: adj[rd].append(ld)
            
            adj[ld].sort(key=lambda neighbor: angle(ld, neighbor))
            adj[rd].sort(key=lambda neighbor: angle(rd, neighbor))

            lc = None
            idx_rd = adj[ld].index(rd)
            for i in range(1, len(adj[ld])):
                cand = adj[ld][(idx_rd + i) % len(adj[ld])]
                if orientation_sign(ld, rd, cand) > 0:
                    lc = cand
                    while True:
                        next_idx = (adj[ld].index(lc) + 1) % len(adj[ld])
                        next_cand = adj[ld][next_idx]
                        if next_cand != rd and orientation_sign(ld, rd, next_cand) > 0 and \
                           in_circle(ld, rd, lc, next_cand):
                            adj[ld].remove(lc)
                            adj[lc].remove(ld)
                            lc = next_cand
                        else:
                            break
                    break
            
            rc = None
            idx_ld = adj[rd].index(ld)
            for i in range(1, len(adj[rd])):
                cand = adj[rd][(idx_ld - i + len(adj[rd])) % len(adj[rd])]
                if orientation_sign(rd, ld, cand) < 0:
                    rc = cand
                    while True:
                        next_idx = (adj[rd].index(rc) - 1 + len(adj[rd])) % len(adj[rd])
                        next_cand = adj[rd][next_idx]
                        if next_cand != ld and orientation_sign(rd, ld, next_cand) < 0 and \
                           in_circle(rd, ld, rc, next_cand):
                            adj[rd].remove(rc)
                            adj[rc].remove(rd)
                            rc = next_cand
                        else:
                            break
                    break

            if not lc and not rc:
                break
            
            if not lc or (rc and in_circle(ld, rd, lc, rc)):
                rd = rc
            else:
                ld = lc

        return adj

