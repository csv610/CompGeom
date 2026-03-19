from __future__ import annotations
import math
from typing import List, Tuple, Optional, Set, Dict
from collections import defaultdict
from compgeom.kernel import Point3D, Plane
from compgeom.mesh.surfmesh.surface_mesh import SurfaceMesh
from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh

class BallPivotingReconstructor:
    """
    Implements the Ball Pivoting Algorithm (BPA) for surface reconstruction.
    """
    def __init__(self, points: List[Point3D], radius: float):
        self.points = points
        self.radius = radius
        self.radius_sq = radius * radius
        self._triangles: List[Tuple[int, int, int]] = []
        self._used_points: Set[int] = set()
        self._edge_front: List[Tuple[int, int, int]] = [] # (v1, v2, v_opposite)
        self._point_to_tets: Dict[int, Set[int]] = defaultdict(set)
        self._edge_to_tri_count: Dict[Tuple[int, int], int] = defaultdict(int)

    def reconstruct(self) -> TriMesh:
        """Runs the reconstruction process and returns a TriMesh."""
        if not self.points:
            return TriMesh([], [])
            
        # 1. Start with a seed triangle
        seed = self._find_seed_triangle()
        if not seed:
            # Try multiple seeds from different starting points if needed
            pass
            
        if seed:
            self._add_triangle(*seed)
        
        # 2. Iteratively pivot around boundary edges
        while self._edge_front:
            v1, v2, v_opp = self._edge_front.pop(0)
            edge = tuple(sorted((v1, v2)))
            
            # If the edge is already shared by two triangles, it's not a boundary
            if self._edge_to_tri_count[edge] >= 2:
                continue
                
            p_idx = self._pivot_around_edge(v1, v2, v_opp)
            if p_idx is not None:
                self._add_triangle(v1, p_idx, v2)
                
        return TriMesh(self.points, self._triangles)

    def _find_seed_triangle(self) -> Optional[Tuple[int, int, int]]:
        """Finds a seed triangle that can support a ball of radius R."""
        n = len(self.points)
        # Use a small subset or spatial grid for better performance in real use
        for i in range(n):
            for j in range(i + 1, n):
                if self._dist_sq(self.points[i], self.points[j]) > 4 * self.radius_sq:
                    continue
                for k in range(j + 1, n):
                    center = self._get_ball_center(i, j, k)
                    if center and self._is_ball_empty(center, {i, j, k}):
                        return (i, j, k)
        return None

    def _pivot_around_edge(self, v1: int, v2: int, v_opp: int) -> Optional[int]:
        """Pivots the ball around the edge (v1, v2) starting from v_opp."""
        p1, p2, po = self.points[v1], self.points[v2], self.points[v_opp]
        c_old = self._get_ball_center(v1, v2, v_opp)
        if not c_old: return None
        
        # Edge vector and midpoint
        edge_vec = p2 - p1
        edge_mid = (p1 + p2) * 0.5
        
        best_point = None
        min_angle = float('inf')
        
        # For each potential point p_k
        for k, pk in enumerate(self.points):
            if k in (v1, v2, v_opp): continue
            
            # Check distance to edge midpoint (early exit)
            if (pk - edge_mid).length_sq() > 4 * self.radius_sq:
                continue
                
            c_new = self._get_ball_center(v1, v2, k)
            if not c_new: continue
            
            # Check if this new ball is empty
            if not self._is_ball_empty(c_new, {v1, v2, k}):
                continue
            
            # Calculate pivoting angle
            # (Simplified angle calculation for demonstration)
            angle = self._calculate_pivot_angle(edge_mid, edge_vec, c_old, c_new)
            if angle < min_angle:
                min_angle = angle
                best_point = k
                
        return best_point

    def _get_ball_center(self, i, j, k) -> Optional[Point3D]:
        """Calculates the center of a ball of radius R resting on points i, j, k."""
        p1, p2, p3 = self.points[i], self.points[j], self.points[k]
        
        # 1. Circumcenter of the triangle in 3D
        # Using a simplified formula
        a = p1 - p3
        b = p2 - p3
        cross = a.cross(b)
        ln_sq = cross.length_sq()
        if ln_sq < 1e-12: return None # Collinear
        
        # Circumradius r
        r = (a.length() * b.length() * (a-b).length()) / (2 * math.sqrt(ln_sq))
        if r > self.radius: return None # Ball too small
        
        # Distance from triangle plane to ball center
        h = math.sqrt(self.radius_sq - r*r)
        
        # Midpoint of circumcircle
        # M = p3 + ((|a|^2 b - |b|^2 a) x (a x b)) / (2 |a x b|^2)
        m = p3 + ( (b * a.length_sq() - a * b.length_sq()).cross(cross) ) * (0.5 / ln_sq)
        
        # Normal to triangle plane
        normal = cross
        normal = normal * (1.0 / math.sqrt(ln_sq))
        
        # Two possible centers, pick one based on orientation
        return m + normal * h

    def _is_ball_empty(self, center: Point3D, ignore_indices: Set[int]) -> bool:
        """Checks if any point (other than ignored) is inside the ball."""
        # Use a spatial query in a real implementation
        for idx, p in enumerate(self.points):
            if idx in ignore_indices: continue
            if (p - center).length_sq() < self.radius_sq - 1e-9:
                return False
        return True

    def _calculate_pivot_angle(self, mid, axis, c1, c2) -> float:
        """Calculates the angle of rotation around 'axis' from c1 to c2."""
        v1 = (c1 - mid)
        v2 = (c2 - mid)
        # Project onto plane perpendicular to axis
        # (Assuming c1, c2 already in that plane by construction)
        dot = v1.dot(v2) / (v1.length() * v2.length())
        dot = max(-1.0, min(1.0, dot))
        return math.acos(dot)

    def _add_triangle(self, i, j, k):
        self._triangles.append((i, j, k))
        # Update edge front
        self._add_to_front(i, j, k)
        self._add_to_front(j, k, i)
        self._add_to_front(k, i, j)
        
        self._edge_to_tri_count[tuple(sorted((i, j)))] += 1
        self._edge_to_tri_count[tuple(sorted((j, k)))] += 1
        self._edge_to_tri_count[tuple(sorted((k, i)))] += 1
        
        self._used_points.update([i, j, k])

    def _add_to_front(self, v1, v2, v_opp):
        edge = tuple(sorted((v1, v2)))
        # In a real BPA, we'd manage the front more carefully (removing edges that become internal)
        self._edge_front.append((v1, v2, v_opp))

    def _dist_sq(self, p1: Point3D, p2: Point3D) -> float:
        return (p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2


class PoissonReconstructor:
    """
    Implements a grid-based Poisson Surface Reconstruction.
    Kazhdan, Bolitho, and Hoppe, "Poisson surface reconstruction", 2006.
    """
    def __init__(self, points: List[Point3D], normals: List[Point3D], resolution: int = 32):
        self.points = points
        self.normals = normals
        self.res = resolution
        
        # 1. Bounding box
        all_x = [p.x for p in points]
        all_y = [p.y for p in points]
        all_z = [p.z for p in points]
        self.bmin = (min(all_x), min(all_y), min(all_z))
        self.bmax = (max(all_x), max(all_y), max(all_z))
        
        # Add padding
        pad = 0.2 * max(self.bmax[i] - self.bmin[i] for i in range(3))
        self.bmin = tuple(v - pad for v in self.bmin)
        self.bmax = tuple(v + pad for v in self.bmax)
        
    def reconstruct(self) -> TriMesh:
        import numpy as np
        from scipy import sparse
        from scipy.sparse.linalg import spsolve
        
        res = self.res
        nx, ny, nz = res, res, res
        dx = (self.bmax[0] - self.bmin[0]) / (nx - 1)
        dy = (self.bmax[1] - self.bmin[1]) / (ny - 1)
        dz = (self.bmax[2] - self.bmin[2]) / (nz - 1)
        
        # 2. Rasterize normals into a vector field V
        V = np.zeros((nx, ny, nz, 3))
        weight = np.zeros((nx, ny, nz))
        
        for p, n in zip(self.points, self.normals):
            ix = int((p.x - self.bmin[0]) / dx)
            iy = int((p.y - self.bmin[1]) / dy)
            iz = int((p.z - self.bmin[2]) / dz)
            
            if 0 <= ix < nx and 0 <= iy < ny and 0 <= iz < nz:
                V[ix, iy, iz, 0] += n.x
                V[ix, iy, iz, 1] += n.y
                V[ix, iy, iz, 2] += n.z
                weight[ix, iy, iz] += 1.0
                
        mask = weight > 0
        V[mask] /= weight[mask][:, np.newaxis]
        
        # 3. Compute divergence of V
        divV = np.zeros((nx, ny, nz))
        divV[:-1, :, :] += (V[1:, :, :, 0] - V[:-1, :, :, 0]) / dx
        divV[:, :-1, :] += (V[:, 1:, :, 1] - V[:, :-1, :, 1]) / dy
        divV[:, :, :-1] += (V[:, :, 1:, 2] - V[:, :, :-1, 2]) / dz
        
        # 4. Solve Poisson equation: L * Phi = div V
        num_nodes = nx * ny * nz
        
        def get_idx(i, j, k):
            return i * (ny * nz) + j * nz + k
            
        rows, cols, data = [], [], []
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    idx = get_idx(i, j, k)
                    
                    if i == 0 or i == nx-1 or j == 0 or j == ny-1 or k == 0 or k == nz-1:
                        rows.append(idx); cols.append(idx); data.append(1.0)
                        divV[i, j, k] = 0
                        continue
                        
                    rows.append(idx); cols.append(idx); data.append(-2/dx**2 - 2/dy**2 - 2/dz**2)
                    rows.append(idx); cols.append(get_idx(i-1, j, k)); data.append(1/dx**2)
                    rows.append(idx); cols.append(get_idx(i+1, j, k)); data.append(1/dx**2)
                    rows.append(idx); cols.append(get_idx(i, j-1, k)); data.append(1/dy**2)
                    rows.append(idx); cols.append(get_idx(i, j+1, k)); data.append(1/dy**2)
                    rows.append(idx); cols.append(get_idx(i, j, k-1)); data.append(1/dz**2)
                    rows.append(idx); cols.append(get_idx(i, j, k+1)); data.append(1/dz**2)
                    
        L = sparse.csc_matrix((data, (rows, cols)), shape=(num_nodes, num_nodes))
        rhs = divV.flatten()
        
        phi_flat = spsolve(L, rhs)
        phi = phi_flat.reshape((nx, ny, nz))
        
        # 5. Isovalue setting
        vals_at_pts = []
        for p in self.points:
            ix = int((p.x - self.bmin[0]) / dx)
            iy = int((p.y - self.bmin[1]) / dy)
            iz = int((p.z - self.bmin[2]) / dz)
            if 0 <= ix < nx and 0 <= iy < ny and 0 <= iz < nz:
                vals_at_pts.append(phi[ix, iy, iz])
        
        isovalue = np.median(vals_at_pts) if vals_at_pts else 0.0
        
        # 6. Extract surface
        from compgeom.mesh.volmesh.marching_cubes import MarchingCubes
        
        def scalar_field(x, y, z):
            ix = (x - self.bmin[0]) / dx
            iy = (y - self.bmin[1]) / dy
            iz = (z - self.bmin[2]) / dz
            i0, j0, k0 = int(ix), int(iy), int(iz)
            if not (0 <= i0 < nx-1 and 0 <= j0 < ny-1 and 0 <= k0 < nz-1): return 0.0
            fx, fy, fz = ix - i0, iy - j0, iz - k0
            
            return (phi[i0, j0, k0] * (1-fx) * (1-fy) * (1-fz) +
                    phi[i0+1, j0, k0] * fx * (1-fy) * (1-fz) +
                    phi[i0, j0+1, k0] * (1-fx) * fy * (1-fz) +
                    phi[i0+1, j0+1, k0] * fx * fy * (1-fz) +
                    phi[i0, j0, k0+1] * (1-fx) * (1-fy) * fz +
                    phi[i0+1, j0, k0+1] * fx * (1-fy) * fz +
                    phi[i0, j0+1, k0+1] * (1-fx) * fy * fz +
                    phi[i0+1, j0+1, k0+1] * fx * fy * fz)

        return MarchingCubes.reconstruct(scalar_field, self.bmin, self.bmax, resolution=res, isovalue=isovalue)
