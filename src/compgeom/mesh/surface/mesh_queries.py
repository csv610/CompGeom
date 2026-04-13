"""Spatial queries: ray intersection and distances."""

from typing import List, Tuple, Optional
import math

from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.kernel import Point3D
from compgeom.intersect import (
    ray_triangle_intersect,
    ray_mesh_intersect,
    mesh_mesh_intersect
)


class MeshQueries:
    """Algorithms for querying spatial relationships with a mesh."""

    @staticmethod
    def ray_intersection_triangle(
        origin: Tuple[float, float, float],
        direction: Tuple[float, float, float],
        v0: Tuple[float, float, float],
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
        epsilon: float = 1e-8,
    ) -> Optional[Tuple[float, float, float]]:
        return ray_triangle_intersect(origin, direction, v0, v1, v2, epsilon)

    @staticmethod
    def _single_ray_face_intersect(
        mesh: SurfaceMesh,
        face_idx: int,
        origin: Tuple[float, float, float],
        direction: Tuple[float, float, float],
    ) -> Optional[float]:
        """Helper to test a single face (polygon) for intersection."""
        face = mesh.faces[face_idx]
        v_indices = face.v_indices
        p0_v = mesh.vertices[v_indices[0]]
        p0 = (p0_v.x, p0_v.y, getattr(p0_v, "z", 0.0))

        min_t = float("inf")
        found = False

        for i in range(1, len(v_indices) - 1):
            p1_v = mesh.vertices[v_indices[i]]
            p2_v = mesh.vertices[v_indices[i + 1]]
            p1 = (p1_v.x, p1_v.y, getattr(p1_v, "z", 0.0))
            p2 = (p2_v.x, p2_v.y, getattr(p2_v, "z", 0.0))

            res = ray_triangle_intersect(origin, direction, p0, p1, p2)
            if res:
                t, u, v = res
                if t < min_t:
                    min_t = t
                    found = True

        return min_t if found else None

    @staticmethod
    def ray_intersect(
        mesh: SurfaceMesh,
        origin: Tuple[float, float, float],
        direction: Tuple[float, float, float],
        use_spatial: bool = True,
    ) -> List[Tuple[int, float]]:
        return ray_mesh_intersect(mesh, origin, direction, use_spatial)

    @staticmethod
    def _point_triangle_dist_sq(
        p: Tuple[float, float, float],
        v0: Tuple[float, float, float],
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
    ) -> float:
        """Calculates exact squared distance from a point to a triangle."""
        # Implementation of point-triangle distance in 3D
        # See Real-Time Collision Detection by Christer Ericson
        a, b, c = v0, v1, v2
        ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        ap = (p[0] - a[0], p[1] - a[1], p[2] - a[2])

        d1 = ab[0] * ap[0] + ab[1] * ap[1] + ab[2] * ap[2]
        d2 = ac[0] * ap[0] + ac[1] * ap[1] + ac[2] * ap[2]
        if d1 <= 0 and d2 <= 0:
            return ap[0] ** 2 + ap[1] ** 2 + ap[2] ** 2

        bp = (p[0] - b[0], p[1] - b[1], p[2] - b[2])
        d3 = ab[0] * bp[0] + ab[1] * bp[1] + b[2] * bp[2]
        d4 = ac[0] * bp[0] + ac[1] * bp[1] + ac[2] * bp[2]
        if d3 >= 0 and d4 <= d3:
            return bp[0] ** 2 + bp[1] ** 2 + bp[2] ** 2

        vc = d1 * d4 - d3 * d2
        if vc <= 0 and d1 >= 0 and d3 <= 0:
            v = d1 / (d1 - d3)
            return (ap[0] - v * ab[0]) ** 2 + (ap[1] - v * ab[1]) ** 2 + (ap[2] - v * ab[2]) ** 2

        cp = (p[0] - c[0], p[1] - c[1], p[2] - c[2])
        d5 = ab[0] * cp[0] + ab[1] * cp[1] + ab[2] * cp[2]
        d6 = ac[0] * cp[0] + ac[1] * cp[1] + ac[2] * cp[2]
        if d6 >= 0 and d5 <= d6:
            return cp[0] ** 2 + cp[1] ** 2 + cp[2] ** 2

        vb = d5 * d2 - d1 * d6
        if vb <= 0 and d2 >= 0 and d6 <= 0:
            w = d2 / (d2 - d6)
            return (ap[0] - w * ac[0]) ** 2 + (ap[1] - w * ac[1]) ** 2 + (ap[2] - w * ac[2]) ** 2

        va = d3 * d6 - d5 * d4
        if va <= 0 and (d4 - d3) >= 0 and (d5 - d6) >= 0:
            w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
            edge = (c[0] - b[0], c[1] - b[1], c[2] - b[2])
            return (bp[0] - w * edge[0]) ** 2 + (bp[1] - w * edge[1]) ** 2 + (bp[2] - w * edge[2]) ** 2

        denom = 1.0 / (va + vb + vc)
        v = vb * denom
        w = vc * denom
        return (
            (ap[0] - v * ab[0] - w * ac[0]) ** 2
            + (ap[1] - v * ab[1] - w * ac[1]) ** 2
            + (ap[2] - v * ab[2] - w * ac[2]) ** 2
        )

    @staticmethod
    def compute_sdf(mesh: SurfaceMesh, point: Tuple[float, float, float], use_spatial: bool = True) -> float:
        """
        Computes the Signed Distance Function (SDF) from a point to the mesh.
        Using exact point-triangle distance.
        """
        px, py, pz = point
        min_dist_sq = float("inf")

        for face in mesh.faces:
            v_indices = face.v_indices
            p0_v = mesh.vertices[v_indices[0]]
            p0 = (p0_v.x, p0_v.y, getattr(p0_v, "z", 0.0))

            for i in range(1, len(v_indices) - 1):
                p1_v = mesh.vertices[v_indices[i]]
                p2_v = mesh.vertices[v_indices[i + 1]]
                p1 = (p1_v.x, p1_v.y, getattr(p1_v, "z", 0.0))
                p2 = (p2_v.x, p2_v.y, getattr(p2_v, "z", 0.0))

                d_sq = MeshQueries._point_triangle_dist_sq(point, p0, p1, p2)
                if d_sq < min_dist_sq:
                    min_dist_sq = d_sq

        distance = math.sqrt(min_dist_sq)
        return distance

    @staticmethod
    def slice_mesh(
        mesh: SurfaceMesh,
        plane_origin: Tuple[float, float, float],
        plane_normal: Tuple[float, float, float],
    ) -> List[Tuple[Point3D, Point3D]]:
        """
        Slices the mesh with a plane and returns a list of line segments (edges).
        """
        nx, ny, nz = plane_normal
        mag = math.sqrt(nx * nx + ny * ny + nz * nz)
        if mag < 1e-9: return []
        nx, ny, nz = nx / mag, ny / mag, nz / mag

        segments = []
        def get_dist(p):
            return (p.x - plane_origin[0]) * nx + (p.y - plane_origin[1]) * ny + (getattr(p, "z", 0.0) - plane_origin[2]) * nz

        for face in mesh.faces:
            v_idx = face.v_indices
            pts = [mesh.vertices[i] for i in v_idx]
            dists = [get_dist(p) for p in pts]
            intersect_pts = []
            for i in range(len(v_idx)):
                u, v = i, (i + 1) % len(v_idx)
                d_u, d_v = dists[u], dists[v]
                if (d_u > 0 and d_v < 0) or (d_u < 0 and d_v > 0):
                    t = abs(d_u) / (abs(d_u) + abs(d_v))
                    p_u, p_v = pts[u], pts[v]
                    ix = p_u.x + t * (p_v.x - p_u.x)
                    iy = p_u.y + t * (p_v.y - p_u.y)
                    iz = getattr(p_u, "z", 0.0) + t * (getattr(p_v, "z", 0.0) - getattr(p_u, "z", 0.0))
                    intersect_pts.append(Point3D(ix, iy, iz))
                elif abs(d_u) < 1e-9:
                    p_u = pts[u]
                    intersect_pts.append(Point3D(p_u.x, p_u.y, getattr(p_u, "z", 0.0)))

            unique_pts = []
            for p in intersect_pts:
                if not any(math.sqrt((p.x - up.x) ** 2 + (p.y - up.y) ** 2 + (p.z - up.z) ** 2) < 1e-8 for up in unique_pts):
                    unique_pts.append(p)
            if len(unique_pts) == 2:
                segments.append((unique_pts[0], unique_pts[1]))
        return segments

    @staticmethod
    def mesh_intersection(mesh_a: SurfaceMesh, mesh_b: SurfaceMesh) -> List[Tuple[int, int]]:
        return mesh_mesh_intersect(mesh_a, mesh_b)

    @staticmethod
    def extract_intersection_lines(mesh_a: SurfaceMesh, mesh_b: SurfaceMesh) -> List[Tuple[Point3D, Point3D]]:
        pass

    @staticmethod
    def generalized_winding_number(mesh: SurfaceMesh, point: Tuple[float, float, float]) -> float:
        wn = 0.0
        px, py, pz = point
        for face in mesh.faces:
            v_indices = face.v_indices
            v0_node = mesh.vertices[v_indices[0]]
            v0 = (v0_node.x - px, v0_node.y - py, getattr(v0_node, "z", 0.0) - pz)
            for i in range(1, len(v_indices) - 1):
                v1_node = mesh.vertices[v_indices[i]]
                v2_node = mesh.vertices[v_indices[i+1]]
                a, b, c = v0, (v1_node.x - px, v1_node.y - py, getattr(v1_node, "z", 0.0) - pz), (v2_node.x - px, v2_node.y - py, getattr(v2_node, "z", 0.0) - pz)
                ma, mb, mc = math.sqrt(sum(x*x for x in a)), math.sqrt(sum(x*x for x in b)), math.sqrt(sum(x*x for x in c))
                det = a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])
                al_b, al_c, bl_c = a[0]*b[0]+a[1]*b[1]+a[2]*b[2], a[0]*c[0]+a[1]*c[1]+a[2]*c[2], b[0]*c[0]+b[1]*c[1]+b[2]*c[2]
                denom = ma*mb*mc + al_b*mc + al_c*mb + bl_c*ma
                wn += 2.0 * math.atan2(det, denom)
        return wn / (4.0 * math.pi)

    @staticmethod
    def poisson_disk_sampling(mesh: SurfaceMesh, min_dist: float, k_attempts: int = 30) -> List[Point3D]:
        return []
