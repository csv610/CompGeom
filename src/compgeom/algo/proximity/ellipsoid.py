from __future__ import annotations

from typing import List

import numpy as np
from scipy.spatial import ConvexHull, Delaunay

from compgeom.kernel import Point3D

from .largest_empty_sphere import find_largest_empty_sphere

__all__ = ["find_largest_empty_oriented_ellipsoid"]


def find_largest_empty_oriented_ellipsoid(points: List[Point3D]) -> dict:

    if len(points) < 4:
        return {
            "volume": 0.0,
            "center": Point3D(0, 0, 0),
            "radii": (0, 0, 0),
            "axes": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        }

    pts_array = np.array([[p.x, p.y, getattr(p, "z", 0.0)] for p in points])
    try:
        hull = ConvexHull(pts_array)
        delaunay = Delaunay(pts_array)
    except Exception:
        return {
            "volume": 0.0,
            "center": Point3D(0, 0, 0),
            "radii": (0, 0, 0),
            "axes": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        }

    seeds = []
    try:
        les_center, les_r = find_largest_empty_sphere(points)
        seeds.append((np.array([les_center.x, les_center.y, les_center.z]), les_r))
    except Exception:
        pass

    # Add top Delaunay centroids as seeds
    for simplex in delaunay.simplices:
        pts = pts_array[simplex]
        c = np.mean(pts, axis=0)
        if delaunay.find_simplex(c) >= 0:
            # Find min dist to points/hull for initial R
            min_d = np.min(np.linalg.norm(pts_array - c, axis=1))
            for eq in hull.equations:
                d_hull = abs(np.dot(eq[:3], c) + eq[3]) / np.linalg.norm(eq[:3])
                if d_hull < min_d:
                    min_d = d_hull
            seeds.append((c, min_d))

    seeds = sorted(seeds, key=lambda x: x[1], reverse=True)[:5]

    orientations = [np.eye(3)]
    centroid = np.mean(pts_array, axis=0)
    cov = np.cov((pts_array - centroid).T)
    _, eigenvectors = np.linalg.eigh(cov)
    orientations.append(eigenvectors.T)  # PCA axes

    for simplex in hull.simplices[:3]:  # Add a few face-aligned axes
        p1, p2, p3 = pts_array[simplex]
        n = np.array(np.cross(p2 - p1, p3 - p1), dtype=float)
        n_norm = np.linalg.norm(n)
        if n_norm > 1e-9:
            n /= n_norm
            t1 = (p2 - p1) / np.linalg.norm(p2 - p1)
            t2 = np.cross(n, t1)
            orientations.append(np.vstack((t1, t2, n)))

    def optimize_ellipsoid(C, U, initial_r):
        # Coordinate descent for a, b, c
        # local coords: P_loc = (P - C) @ U.T
        P_loc = (pts_array - C) @ U.T
        # Plane eqs in local coords: A*x + B*y + C*z + D = 0
        hull_eq_loc = []
        for eq in hull.equations:
            Ng, Dg = eq[:3], eq[3]
            Al, Bl, Cl = np.dot(Ng, U[0]), np.dot(Ng, U[1]), np.dot(Ng, U[2])
            Dl = np.dot(Ng, C) + Dg
            hull_eq_loc.append([Al, Bl, Cl, Dl])

        # Start with a small sphere
        abc = np.array([initial_r, initial_r, initial_r], dtype=float) * 0.95

        for _ in range(10):  # Iterations of coordinate descent
            for i in range(3):
                # Maximize abc[i]
                other_idx = [j for j in range(3) if j != i]

                max_val_sq = float("inf")

                # Point constraints: (x/a)^2 + (y/b)^2 + (z/c)^2 >= 1
                # (val/abc[i])^2 >= 1 - sum((other_val/abc[other])^2)
                for p in P_loc:
                    sum_others = (p[other_idx[0]] / abc[other_idx[0]]) ** 2 + (
                        p[other_idx[1]] / abc[other_idx[1]]
                    ) ** 2
                    if sum_others < 1.0:
                        limit_sq = (p[i] ** 2) / (1.0 - sum_others)
                        if limit_sq < max_val_sq:
                            max_val_sq = limit_sq

                # Plane constraints: sum((Coeff[j] * abc[j])^2) <= D^2
                for eq in hull_eq_loc:
                    Ai = eq[i]
                    SumOthers = (eq[other_idx[0]] * abc[other_idx[0]]) ** 2 + (
                        eq[other_idx[1]] * abc[other_idx[1]]
                    ) ** 2
                    D_sq = eq[3] ** 2
                    if Ai**2 > 1e-12:
                        if D_sq > SumOthers:
                            limit_sq = (D_sq - SumOthers) / (Ai**2)
                            if limit_sq < max_val_sq:
                                max_val_sq = limit_sq
                        else:
                            max_val_sq = 0.0  # Already intersecting

                if max_val_sq <= 0:
                    abc[i] = 1e-6
                else:
                    abc[i] = np.sqrt(max_val_sq) * 0.999  # Small buffer

        vol = (4 / 3) * np.pi * abc[0] * abc[1] * abc[2]
        return abc, vol

    best_vol = -1.0
    best_res = None

    for C, r in seeds:
        for U in orientations:
            abc, vol = optimize_ellipsoid(C, U, r)
            if vol > best_vol:
                best_vol = vol
                best_res = (C, U, abc)

    if not best_res:
        return {
            "volume": 0.0,
            "center": Point3D(0, 0, 0),
            "radii": (0, 0, 0),
            "axes": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        }

    C, U, abc = best_res
    return {
        "center": Point3D(C[0], C[1], C[2]),
        "radii": tuple(float(x) for x in abc),
        "axes": (
            tuple(float(x) for x in U[0]),
            tuple(float(x) for x in U[1]),
            tuple(float(x) for x in U[2]),
        ),
        "volume": best_vol,
    }
