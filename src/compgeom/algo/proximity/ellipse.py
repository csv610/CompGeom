from __future__ import annotations

from typing import List

import numpy as np
from scipy.spatial import ConvexHull, Delaunay

from compgeom.kernel import Point2D

from .largest_empty_circle import find_largest_empty_circle

__all__ = ["find_largest_empty_oriented_ellipse"]


def find_largest_empty_oriented_ellipse(points: List[Point2D]) -> dict:

    if len(points) < 3:
        return {"area": 0.0, "center": Point2D(0, 0), "radii": (0, 0), "angle": 0.0}

    pts_array = np.array([[p.x, p.y] for p in points])
    try:
        hull = ConvexHull(pts_array)
        delaunay = Delaunay(pts_array)
    except Exception:
        return {"area": 0.0, "center": Point2D(0, 0), "radii": (0, 0), "angle": 0.0}

    seeds = []
    try:
        lec_center, lec_r = find_largest_empty_circle(points)
        seeds.append((np.array([lec_center.x, lec_center.y]), lec_r))
    except Exception:
        pass

    for simplex in delaunay.simplices:
        pts = pts_array[simplex]
        c = np.mean(pts, axis=0)
        if delaunay.find_simplex(c) >= 0:
            min_d = np.min(np.linalg.norm(pts_array - c, axis=1))
            for eq in hull.equations:
                d_hull = abs(np.dot(eq[:2], c) + eq[2]) / np.linalg.norm(eq[:2])
                if d_hull < min_d:
                    min_d = d_hull
            seeds.append((c, min_d))

    seeds = sorted(seeds, key=lambda x: x[1], reverse=True)[:5]

    orientations = [np.eye(2)]
    centroid = np.mean(pts_array, axis=0)
    cov = np.cov((pts_array - centroid).T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx = eigenvalues.argsort()[::-1]
    orientations.append(eigenvectors[:, idx].T)

    for simplex in hull.simplices[:5]:
        p1, p2 = pts_array[simplex]
        v = p2 - p1
        v_norm = np.linalg.norm(v)
        if v_norm > 1e-9:
            t1 = v / v_norm
            t2 = np.array([-t1[1], t1[0]])
            orientations.append(np.vstack((t1, t2)))

    def optimize_ellipse(C, U, initial_r):
        P_loc = (pts_array - C) @ U.T
        hull_eq_loc = []
        for eq in hull.equations:
            Ng, Dg = eq[:2], eq[2]
            Al, Bl = np.dot(Ng, U[0]), np.dot(Ng, U[1])
            Dl = np.dot(Ng, C) + Dg
            hull_eq_loc.append([Al, Bl, Dl])

        ab = np.array([initial_r, initial_r], dtype=float) * 0.95

        for _ in range(10):
            for i in range(2):
                other_idx = 1 - i
                max_val_sq = float("inf")

                for p in P_loc:
                    other_term = (p[other_idx] / ab[other_idx]) ** 2
                    if other_term < 1.0:
                        limit_sq = (p[i] ** 2) / (1.0 - other_term)
                        if limit_sq < max_val_sq:
                            max_val_sq = limit_sq

                for eq in hull_eq_loc:
                    Ai = eq[i]
                    OtherTerm = (eq[other_idx] * ab[other_idx]) ** 2
                    D_sq = eq[2] ** 2
                    if Ai**2 > 1e-12:
                        if D_sq > OtherTerm:
                            limit_sq = (D_sq - OtherTerm) / (Ai**2)
                            if limit_sq < max_val_sq:
                                max_val_sq = limit_sq
                        else:
                            max_val_sq = 0.0

                if max_val_sq <= 0:
                    ab[i] = 1e-6
                else:
                    ab[i] = np.sqrt(max_val_sq) * 0.999

        area = np.pi * ab[0] * ab[1]
        return ab, area

    best_area = -1.0
    best_res = None

    for C, r in seeds:
        for U in orientations:
            ab, area = optimize_ellipse(C, U, r)
            if area > best_area:
                best_area = area
                best_res = (C, U, ab)

    if not best_res:
        return {"area": 0.0, "center": Point2D(0, 0), "radii": (0, 0), "angle": 0.0}

    C, U, ab = best_res
    angle = np.arctan2(U[0][1], U[0][0])
    return {
        "center": Point2D(C[0], C[1]),
        "radii": (float(ab[0]), float(ab[1])),
        "angle": float(angle),
        "area": best_area,
        "axes": (tuple(float(x) for x in U[0]), tuple(float(x) for x in U[1])),
    }
