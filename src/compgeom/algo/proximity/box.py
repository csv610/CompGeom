from __future__ import annotations

from typing import List

import numpy as np
from scipy.spatial import ConvexHull, Delaunay

from compgeom.kernel import Point3D

from .largest_empty_sphere import find_largest_empty_sphere

__all__ = ["find_largest_empty_oriented_box"]


def find_largest_empty_oriented_box(points: List[Point3D]) -> dict:

    if len(points) < 4:
        return {
            "volume": 0.0,
            "center": Point3D(0, 0, 0),
            "width": 0.0,
            "height": 0.0,
            "depth": 0.0,
            "axes": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            "corners": [],
        }

    pts_array = np.array([[p.x, p.y, getattr(p, "z", 0.0)] for p in points])
    try:
        hull = ConvexHull(pts_array)
        delaunay = Delaunay(pts_array)
    except Exception:
        return {
            "volume": 0.0,
            "center": Point3D(0, 0, 0),
            "width": 0.0,
            "height": 0.0,
            "depth": 0.0,
            "axes": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            "corners": [],
        }

    seeds = []

    # 1. Largest Empty Sphere center
    try:
        les_center, _ = find_largest_empty_sphere(points)
        seeds.append(np.array([les_center.x, les_center.y, les_center.z]))
    except Exception:
        pass

    # 2. Top Delaunay tetrahedra
    vols = []
    centroids = []
    for simplex in delaunay.simplices:
        pts = pts_array[simplex]
        vol = abs(np.linalg.det(np.vstack((pts.T, np.ones(4))))) / 6.0
        vols.append(vol)
        centroids.append(np.mean(pts, axis=0))

    top_indices = np.argsort(vols)[-10:]
    for idx in top_indices:
        c = centroids[idx]
        if delaunay.find_simplex(c) >= 0:
            seeds.append(c)

    orientations = []
    orientations.append(np.eye(3))

    centroid = np.mean(pts_array, axis=0)
    cov = np.cov((pts_array - centroid).T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx = eigenvalues.argsort()[::-1]
    pca_axes = eigenvectors[:, idx].T
    orientations.append(pca_axes)

    face_areas = []
    for simplex in hull.simplices:
        p1, p2, p3 = pts_array[simplex]
        area = np.linalg.norm(np.cross(p2 - p1, p3 - p1)) * 0.5
        face_areas.append(area)

    top_faces = np.argsort(face_areas)[-3:]
    for idx in top_faces:
        p1, p2, p3 = pts_array[hull.simplices[idx]]
        n = np.array(np.cross(p2 - p1, p3 - p1), dtype=float)
        norm_n = np.linalg.norm(n)
        if norm_n > 1e-9:
            n = n / norm_n
            t1 = p2 - p1
            norm_t1 = np.linalg.norm(t1)
            if norm_t1 > 1e-9:
                t1 = t1 / norm_t1
                t2 = np.cross(n, t1)
                orientations.append(np.vstack((t1, t2, n)))

    def expand_box(points_loc, hull_eq_loc, order, initial_R):
        bounds = [
            -initial_R,
            initial_R,
            -initial_R,
            initial_R,
            -initial_R,
            initial_R,
        ]
        eps = 1e-7
        for d in order:
            if d == "+x":
                p_lim = float("inf")
                for p in points_loc:
                    if (
                        p[0] > bounds[1] + eps
                        and bounds[2] - eps <= p[1] <= bounds[3] + eps
                        and bounds[4] - eps <= p[2] <= bounds[5] + eps
                    ):
                        if p[0] < p_lim:
                            p_lim = p[0]
                h_lim = float("inf")
                for eq in hull_eq_loc:
                    A, B, C, D = eq
                    if A > eps:
                        for y in [bounds[2], bounds[3]]:
                            for z in [bounds[4], bounds[5]]:
                                val = (-D - B * y - C * z) / A
                                if val < h_lim:
                                    h_lim = val
                bounds[1] = min(p_lim, h_lim) - eps

            elif d == "-x":
                p_lim = -float("inf")
                for p in points_loc:
                    if (
                        p[0] < bounds[0] - eps
                        and bounds[2] - eps <= p[1] <= bounds[3] + eps
                        and bounds[4] - eps <= p[2] <= bounds[5] + eps
                    ):
                        if p[0] > p_lim:
                            p_lim = p[0]
                h_lim = -float("inf")
                for eq in hull_eq_loc:
                    A, B, C, D = eq
                    if A < -eps:
                        for y in [bounds[2], bounds[3]]:
                            for z in [bounds[4], bounds[5]]:
                                val = (-D - B * y - C * z) / A
                                if val > h_lim:
                                    h_lim = val
                bounds[0] = max(p_lim, h_lim) + eps

            elif d == "+y":
                p_lim = float("inf")
                for p in points_loc:
                    if (
                        p[1] > bounds[3] + eps
                        and bounds[0] - eps <= p[0] <= bounds[1] + eps
                        and bounds[4] - eps <= p[2] <= bounds[5] + eps
                    ):
                        if p[1] < p_lim:
                            p_lim = p[1]
                h_lim = float("inf")
                for eq in hull_eq_loc:
                    A, B, C, D = eq
                    if B > eps:
                        for x in [bounds[0], bounds[1]]:
                            for z in [bounds[4], bounds[5]]:
                                val = (-D - A * x - C * z) / B
                                if val < h_lim:
                                    h_lim = val
                bounds[3] = min(p_lim, h_lim) - eps

            elif d == "-y":
                p_lim = -float("inf")
                for p in points_loc:
                    if (
                        p[1] < bounds[2] - eps
                        and bounds[0] - eps <= p[0] <= bounds[1] + eps
                        and bounds[4] - eps <= p[2] <= bounds[5] + eps
                    ):
                        if p[1] > p_lim:
                            p_lim = p[1]
                h_lim = -float("inf")
                for eq in hull_eq_loc:
                    A, B, C, D = eq
                    if B < -eps:
                        for x in [bounds[0], bounds[1]]:
                            for z in [bounds[4], bounds[5]]:
                                val = (-D - A * x - C * z) / B
                                if val > h_lim:
                                    h_lim = val
                bounds[2] = max(p_lim, h_lim) + eps

            elif d == "+z":
                p_lim = float("inf")
                for p in points_loc:
                    if (
                        p[2] > bounds[5] + eps
                        and bounds[0] - eps <= p[0] <= bounds[1] + eps
                        and bounds[2] - eps <= p[1] <= bounds[3] + eps
                    ):
                        if p[2] < p_lim:
                            p[2] = p[2]
                        if p[2] < p_lim:
                            p_lim = p[2]
                h_lim = float("inf")
                for eq in hull_eq_loc:
                    A, B, C, D = eq
                    if C > eps:
                        for x in [bounds[0], bounds[1]]:
                            for y in [bounds[2], bounds[3]]:
                                val = (-D - A * x - B * y) / C
                                if val < h_lim:
                                    h_lim = val
                bounds[5] = min(p_lim, h_lim) - eps

            elif d == "-z":
                p_lim = -float("inf")
                for p in points_loc:
                    if (
                        p[2] < bounds[4] - eps
                        and bounds[0] - eps <= p[0] <= bounds[1] + eps
                        and bounds[2] - eps <= p[1] <= bounds[3] + eps
                    ):
                        if p[2] > p_lim:
                            p_lim = p[2]
                h_lim = -float("inf")
                for eq in hull_eq_loc:
                    A, B, C, D = eq
                    if C < -eps:
                        for x in [bounds[0], bounds[1]]:
                            for y in [bounds[2], bounds[3]]:
                                val = (-D - A * x - B * y) / C
                                if val > h_lim:
                                    h_lim = val
                bounds[4] = max(p_lim, h_lim) + eps

        bounds = [
            min(0, bounds[0]),
            max(0, bounds[1]),
            min(0, bounds[2]),
            max(0, bounds[3]),
            min(0, bounds[4]),
            max(0, bounds[5]),
        ]
        vol = (
            (bounds[1] - bounds[0])
            * (bounds[3] - bounds[2])
            * (bounds[5] - bounds[4])
        )
        return bounds, vol

    best_vol = -1.0
    best_box = None

    orders = [
        ["+x", "-x", "+y", "-y", "+z", "-z"],
        ["+y", "-y", "+z", "-z", "+x", "-x"],
        ["+z", "-z", "+x", "-x", "+y", "-y"],
        ["-x", "+x", "-y", "+y", "-z", "+z"],
        ["-y", "+y", "-z", "+z", "-x", "+x"],
        ["-z", "+z", "-x", "+x", "-y", "+y"],
    ]

    for C in seeds:
        r_nearest = float("inf")
        for p in pts_array:
            d = np.linalg.norm(p - C)
            if d > 1e-9 and d < r_nearest:
                r_nearest = d
        for eq in hull.equations:
            d = -(np.dot(eq[:3], C) + eq[3]) / np.linalg.norm(eq[:3])
            if d > 1e-9 and d < r_nearest:
                r_nearest = d

        if r_nearest == float("inf"):
            r_nearest = 0.0
        initial_R = (r_nearest / np.sqrt(3.0)) * 0.98

        for U in orientations:
            P_loc = (pts_array - C) @ U.T

            hull_eq_loc = []
            for eq in hull.equations:
                Ng = eq[:3]
                Dg = eq[3]
                Al = np.dot(Ng, U[0])
                Bl = np.dot(Ng, U[1])
                Cl = np.dot(Ng, U[2])
                Dl = np.dot(Ng, C) + Dg
                hull_eq_loc.append([Al, Bl, Cl, Dl])

            for order in orders:
                bounds, vol = expand_box(P_loc, hull_eq_loc, order, initial_R)
                if vol > best_vol:
                    best_vol = vol
                    best_box = (C, U, bounds)

    if not best_box:
        return {
            "volume": 0.0,
            "center": Point3D(0, 0, 0),
            "width": 0.0,
            "height": 0.0,
            "depth": 0.0,
            "axes": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            "corners": [],
        }

    C, U, bounds = best_box
    cx_loc = (bounds[0] + bounds[1]) / 2.0
    cy_loc = (bounds[2] + bounds[3]) / 2.0
    cz_loc = (bounds[4] + bounds[5]) / 2.0

    w = bounds[1] - bounds[0]
    h = bounds[3] - bounds[2]
    d = bounds[5] - bounds[4]

    center_global = C + cx_loc * U[0] + cy_loc * U[1] + cz_loc * U[2]
    center = Point3D(center_global[0], center_global[1], center_global[2])

    corners = []
    for dx in [-w / 2, w / 2]:
        for dy in [-h / 2, h / 2]:
            for dz in [-d / 2, d / 2]:
                cg = center_global + dx * U[0] + dy * U[1] + dz * U[2]
                corners.append(Point3D(cg[0], cg[1], cg[2]))

    return {
        "center": center,
        "width": w,
        "height": h,
        "depth": d,
        "volume": best_vol,
        "axes": (
            tuple(float(x) for x in U[0]),
            tuple(float(x) for x in U[1]),
            tuple(float(x) for x in U[2]),
        ),
        "corners": corners,
    }
