from __future__ import annotations

from typing import List

import numpy as np
from scipy.spatial import ConvexHull, Delaunay

from compgeom.kernel import Point2D

from .largest_empty_circle import find_largest_empty_circle

__all__ = ["find_largest_empty_oriented_rectangle"]


def find_largest_empty_oriented_rectangle(points: List[Point2D]) -> dict:

    if len(points) < 3:
        return {
            "area": 0.0,
            "center": Point2D(0, 0),
            "width": 0.0,
            "height": 0.0,
            "angle": 0.0,
            "corners": [],
        }

    pts_array = np.array([[p.x, p.y] for p in points])
    try:
        hull = ConvexHull(pts_array)
        delaunay = Delaunay(pts_array)
    except Exception:
        return {
            "area": 0.0,
            "center": Point2D(0, 0),
            "width": 0.0,
            "height": 0.0,
            "angle": 0.0,
            "corners": [],
        }

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

    seeds = sorted(seeds, key=lambda x: x[1], reverse=True)[:10]

    orientations = [np.eye(2)]
    centroid = np.mean(pts_array, axis=0)
    cov = np.cov((pts_array - centroid).T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx = eigenvalues.argsort()[::-1]
    orientations.append(eigenvectors[:, idx].T)

    for simplex in hull.simplices:
        p1, p2 = pts_array[simplex]
        v = p2 - p1
        v_norm = np.linalg.norm(v)
        if v_norm > 1e-9:
            t1 = v / v_norm
            t2 = np.array([-t1[1], t1[0]])
            orientations.append(np.vstack((t1, t2)))

    def expand_rect(C, U, initial_r):
        P_loc = (pts_array - C) @ U.T
        hull_eq_loc = []
        for eq in hull.equations:
            Ng, Dg = eq[:2], eq[2]
            Al, Bl = np.dot(Ng, U[0]), np.dot(Ng, U[1])
            Dl = np.dot(Ng, C) + Dg
            hull_eq_loc.append([Al, Bl, Dl])

        side = (initial_r / np.sqrt(2.0)) * 0.95
        bounds = [-side, side, -side, side]

        orders = [
            ["+x", "-x", "+y", "-y"],
            ["+y", "-y", "+x", "-x"],
            ["-x", "+x", "-y", "+y"],
            ["-y", "+y", "-x", "+x"],
        ]
        best_local_area = -1.0
        best_local_bounds = bounds

        eps = 1e-7
        for order in orders:
            cur_bounds = list(bounds)
            for d in order:
                if d == "+x":
                    p_lim = float("inf")
                    for p in P_loc:
                        if (
                            p[0] > cur_bounds[1] + eps
                            and cur_bounds[2] - eps <= p[1] <= cur_bounds[3] + eps
                        ):
                            if p[0] < p_lim:
                                p_lim = p[0]
                    h_lim = float("inf")
                    for eq in hull_eq_loc:
                        if eq[0] > eps:
                            for y in [cur_bounds[2], cur_bounds[3]]:
                                val = (-eq[2] - eq[1] * y) / eq[0]
                                if val < h_lim:
                                    h_lim = val
                    cur_bounds[1] = min(p_lim, h_lim) - eps
                elif d == "-x":
                    p_lim = -float("inf")
                    for p in P_loc:
                        if (
                            p[0] < cur_bounds[0] - eps
                            and cur_bounds[2] - eps <= p[1] <= cur_bounds[3] + eps
                        ):
                            if p[0] > p_lim:
                                p_lim = p[0]
                    h_lim = -float("inf")
                    for eq in hull_eq_loc:
                        if eq[0] < -eps:
                            for y in [cur_bounds[2], cur_bounds[3]]:
                                val = (-eq[2] - eq[1] * y) / eq[0]
                                if val > h_lim:
                                    h_lim = val
                    cur_bounds[0] = max(p_lim, h_lim) + eps
                elif d == "+y":
                    p_lim = float("inf")
                    for p in P_loc:
                        if (
                            p[1] > cur_bounds[3] + eps
                            and cur_bounds[0] - eps <= p[0] <= cur_bounds[1] + eps
                        ):
                            if p[1] < p_lim:
                                p_lim = p[1]
                    h_lim = float("inf")
                    for eq in hull_eq_loc:
                        if eq[1] > eps:
                            for x in [cur_bounds[0], cur_bounds[1]]:
                                val = (-eq[2] - eq[0] * x) / eq[1]
                                if val < h_lim:
                                    h_lim = val
                    cur_bounds[3] = min(p_lim, h_lim) - eps
                elif d == "-y":
                    p_lim = -float("inf")
                    for p in P_loc:
                        if (
                            p[1] < cur_bounds[2] - eps
                            and cur_bounds[0] - eps <= p[0] <= cur_bounds[1] + eps
                        ):
                            if p[1] > p_lim:
                                p_lim = p[1]
                    h_lim = -float("inf")
                    for eq in hull_eq_loc:
                        if eq[1] < -eps:
                            for x in [cur_bounds[0], cur_bounds[1]]:
                                val = (-eq[2] - eq[0] * x) / eq[1]
                                if val > h_lim:
                                    h_lim = val
                    cur_bounds[2] = max(p_lim, h_lim) + eps

            area = (cur_bounds[1] - cur_bounds[0]) * (cur_bounds[3] - cur_bounds[2])
            if area > best_local_area:
                best_local_area = area
                best_local_bounds = cur_bounds
        return best_local_bounds, best_local_area

    best_area = -1.0
    best_res = None

    for C, r in seeds:
        for U in orientations:
            bounds, area = expand_rect(C, U, r)
            if area > best_area:
                best_area = area
                best_res = (C, U, bounds)

    if not best_res:
        return {
            "area": 0.0,
            "center": Point2D(0, 0),
            "width": 0.0,
            "height": 0.0,
            "angle": 0.0,
            "corners": [],
        }

    C, U, bounds = best_res
    cx_loc, cy_loc = (bounds[0] + bounds[1]) / 2.0, (bounds[2] + bounds[3]) / 2.0
    c_global = C + cx_loc * U[0] + cy_loc * U[1]
    w, h = bounds[1] - bounds[0], bounds[3] - bounds[2]
    angle = np.arctan2(U[0][1], U[0][0])
    corners = [
        Point2D(p[0], p[1])
        for p in [
            c_global + dx * U[0] + dy * U[1]
            for dx, dy in [
                (-w / 2, -h / 2),
                (w / 2, -h / 2),
                (w / 2, h / 2),
                (-w / 2, h / 2),
            ]
        ]
    ]
    return {
        "center": Point2D(c_global[0], c_global[1]),
        "width": w,
        "height": h,
        "area": best_area,
        "angle": float(angle),
        "corners": corners,
    }
