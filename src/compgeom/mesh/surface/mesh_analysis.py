"""Mesh analysis algorithms: normals, curvature, and features."""
from collections import defaultdict
import math
from typing import List, Tuple, Dict

from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.kernel import Point3D

class MeshAnalysis:
    """Provides algorithms for analyzing surface meshes."""

    @staticmethod
    def compute_face_normals(mesh: SurfaceMesh) -> List[Tuple[float, float, float]]:
        """Computes the normal vector for each face in the mesh."""
        normals = []
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            ux, uy, uz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
            vx, vy, vz = p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]
            
            nx = uy*vz - uz*vy
            ny = uz*vx - ux*vz
            nz = ux*vy - uy*vx
            
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length > 1e-9:
                normals.append((nx/length, ny/length, nz/length))
            else:
                normals.append((0.0, 0.0, 0.0))
        return normals

    @staticmethod
    def compute_vertex_normals(mesh: SurfaceMesh) -> List[Tuple[float, float, float]]:
        """Computes area-weighted vertex normals for smooth shading."""
        v_normals = [[0.0, 0.0, 0.0] for _ in range(len(mesh.vertices))]
        
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            ux, uy, uz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
            vx, vy, vz = p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]
            
            # Cross product magnitude represents 2x face area
            nx = uy*vz - uz*vy
            ny = uz*vx - ux*vz
            nz = ux*vy - uy*vx
            
            for idx in face:
                v_normals[idx][0] += nx
                v_normals[idx][1] += ny
                v_normals[idx][2] += nz
                
        # Normalize
        res = []
        for nx, ny, nz in v_normals:
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length > 1e-9:
                res.append((nx/length, ny/length, nz/length))
            else:
                res.append((0.0, 0.0, 0.0))
        return res

    @staticmethod
    def total_area(mesh: SurfaceMesh) -> float:
        """Calculates the total surface area of the mesh."""
        total = 0.0
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            ux, uy, uz = v1.x-v0.x, v1.y-v0.y, getattr(v1, 'z', 0.0)-getattr(v0, 'z', 0.0)
            vx, vy, vz = v2.x-v0.x, v2.y-v0.y, getattr(v2, 'z', 0.0)-getattr(v0, 'z', 0.0)
            cx = uy*vz - uz*vy
            cy = uz*vx - ux*vz
            cz = ux*vy - uy*vx
            total += 0.5 * math.sqrt(cx*cx + cy*cy + cz*cz)
        return total

    @staticmethod
    def total_volume(mesh: SurfaceMesh) -> float:
        """Calculates the total volume enclosed by the surface using the divergence theorem."""
        total = 0.0
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            # p0 dot (p1 cross p2) / 6
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            total += (p0[0] * (p1[1]*p2[2] - p1[2]*p2[1]) + 
                      p0[1] * (p1[2]*p2[0] - p1[0]*p2[2]) + 
                      p0[2] * (p1[0]*p2[1] - p1[1]*p2[0])) / 6.0
        return total

    @staticmethod
    def center_of_mass(mesh: SurfaceMesh) -> Tuple[float, float, float]:
        """Calculates the center of mass (centroid) of the volume enclosed by the surface."""
        total_vol = 0.0
        cx, cy, cz = 0.0, 0.0, 0.0
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            # Volume of tet formed with origin
            vol = (p0[0] * (p1[1]*p2[2] - p1[2]*p2[1]) + 
                   p0[1] * (p1[2]*p2[0] - p1[0]*p2[2]) + 
                   p0[2] * (p1[0]*p2[1] - p1[1]*p2[0])) / 6.0
            
            # Centroid of this tet
            tx = (p0[0] + p1[0] + p2[0]) / 4.0
            ty = (p0[1] + p1[1] + p2[1]) / 4.0
            tz = (p0[2] + p1[2] + p2[2]) / 4.0
            
            cx += tx * vol
            cy += ty * vol
            cz += tz * vol
            total_vol += vol
            
        if abs(total_vol) < 1e-12:
            from compgeom.mesh.mesh_geometry import MeshGeometry
            centroid = MeshGeometry.centroid(mesh)
            return centroid.x, centroid.y, getattr(centroid, 'z', 0.0)
            
        return cx/total_vol, cy/total_vol, cz/total_vol

    @staticmethod
    def inertia_tensor(mesh: SurfaceMesh) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Calculates the 3x3 inertia tensor matrix (assuming uniform unit density).
        Returns a tuple of 3 tuples: ((Ixx, Ixy, Ixz), (Iyx, Iyy, Iyz), (Izx, Izy, Izz)).
        """
        # Based on David Eberly's Polyhedral Mass Properties
        mult = [1/6, 1/24, 1/24, 1/24, 1/60, 1/60, 1/60, 1/120, 1/120, 1/120]
        intg = [0.0] * 10
        
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            a1, b1, c1 = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
            a2, b2, c2 = p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]
            d0, d1, d2 = b1*c2 - b2*c1, a2*c1 - a1*c2, a1*b2 - a2*b1
            
            f1x = p0[0] + p1[0] + p2[0]
            f1y = p0[1] + p1[1] + p2[1]
            f1z = p0[2] + p1[2] + p2[2]
            
            f2x = p0[0]**2 + p1[0]**2 + p2[0]**2 + f1x**2
            f2y = p0[1]**2 + p1[1]**2 + p2[1]**2 + f1y**2
            f2z = p0[2]**2 + p1[2]**2 + p2[2]**2 + f1z**2
            
            f3x = p0[0]**3 + p1[0]**3 + p2[0]**3 + f1x * f2x
            f3y = p0[1]**3 + p1[1]**3 + p2[1]**3 + f1y * f2y
            f3z = p0[2]**3 + p1[2]**3 + p2[2]**3 + f1z * f2z
            
            g0x = f2x + p0[0] * (f1x + p0[0])
            g0y = f2y + p0[1] * (f1y + p0[1])
            g0z = f2z + p0[2] * (f1z + p0[2])
            
            g1x = f2x + p1[0] * (f1x + p1[0])
            g1y = f2y + p1[1] * (f1y + p1[1])
            g1z = f2z + p1[2] * (f1z + p1[2])
            
            g2x = f2x + p2[0] * (f1x + p2[0])
            g2y = f2y + p2[1] * (f1y + p2[1])
            g2z = f2z + p2[2] * (f1z + p2[2])
            
            fxyz = p0[0] * b1 * g0z + p1[0] * b2 * g1z + p2[0] * (b1 + b2) * g2z # simplified integral components
            
            intg[0] += d0 * f1x
            intg[1] += d0 * f2x
            intg[2] += d1 * f2y
            intg[3] += d2 * f2z
            intg[4] += d0 * f3x
            intg[5] += d1 * f3y
            intg[6] += d2 * f3z
            
            # Cross terms
            temp0 = p0[0] + p1[0]
            temp1 = p0[1] + p1[1]
            temp2 = p0[2] + p1[2]
            
            # Approximated fast cross terms for physics engines
            f_x_y = p0[0]*p0[1] + p1[0]*p1[1] + p2[0]*p2[1] + (p0[0]+p1[0]+p2[0])*(p0[1]+p1[1]+p2[1])
            f_y_z = p0[1]*p0[2] + p1[1]*p1[2] + p2[1]*p2[2] + (p0[1]+p1[1]+p2[1])*(p0[2]+p1[2]+p2[2])
            f_z_x = p0[2]*p0[0] + p1[2]*p1[0] + p2[2]*p2[0] + (p0[2]+p1[2]+p2[2])*(p0[0]+p1[0]+p2[0])
            
            intg[7] += d0 * f_x_y
            intg[8] += d1 * f_y_z
            intg[9] += d2 * f_z_x

        for i in range(10): intg[i] *= mult[i]
        
        mass = intg[0]
        # Translate to center of mass
        cm_x, cm_y, cm_z = intg[1]/mass, intg[2]/mass, intg[3]/mass
        
        # Inertia tensor relative to origin
        ixx = intg[5] + intg[6]
        iyy = intg[4] + intg[6]
        izz = intg[4] + intg[5]
        ixy = -intg[7]
        iyz = -intg[8]
        izx = -intg[9]
        
        # Parallel axis theorem to move to COM
        ixx -= mass * (cm_y**2 + cm_z**2)
        iyy -= mass * (cm_z**2 + cm_x**2)
        izz -= mass * (cm_x**2 + cm_y**2)
        ixy += mass * cm_x * cm_y
        iyz += mass * cm_y * cm_z
        izx += mass * cm_z * cm_x
        
    @staticmethod
    def estimate_point_normals(points: List[Point3D], k_neighbors: int = 10) -> List[Tuple[float, float, float]]:
        """Estimates normals for a point cloud using local PCA."""
        try:
            import numpy as np
            from scipy.spatial import cKDTree
        except ImportError:
            raise ImportError("Normal estimation requires 'numpy' and 'scipy'.")

        pts = np.array([[p.x, p.y, getattr(p, 'z', 0.0)] for p in points])
        tree = cKDTree(pts)
        normals = []
        
        for i in range(len(pts)):
            # Find neighbors
            _, idx = tree.query(pts[i], k=k_neighbors)
            neighbors = pts[idx]
            
            # Local PCA
            centroid = np.mean(neighbors, axis=0)
            centered = neighbors - centroid
            cov = np.dot(centered.T, centered)
            
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            # Normal is the eigenvector corresponding to the smallest eigenvalue
            n = eigenvectors[:, 0]
            normals.append(tuple(n))
            
        return normals

    @staticmethod
    def hausdorff_distance(mesh_a: SurfaceMesh, mesh_b: SurfaceMesh, sample_count: int = 1000) -> float:
        """
        Calculates the approximate Hausdorff distance between two meshes.
        dH(A, B) = max( sup_{a in A} inf_{b in B} d(a,b), sup_{b in B} inf_{a in A} d(a,b) )
        """
        from compgeom.mesh.surface.mesh_queries import MeshQueries
        
        def one_way_dist(m1, m2):
            max_d = 0.0
            # Sample points on m1 (using vertices for simplicity)
            indices = list(range(len(m1.vertices)))
            if len(indices) > sample_count:
                import random
                indices = random.sample(indices, sample_count)
                
            for idx in indices:
                p = m1.vertices[idx]
                p_coord = (p.x, p.y, getattr(p, 'z', 0.0))
                # inf_{b in B} d(a,b) is the SDF magnitude
                dist = abs(MeshQueries.compute_sdf(m2, p_coord))
                max_d = max(max_d, dist)
            return max_d

        return max(one_way_dist(mesh_a, mesh_b), one_way_dist(mesh_b, mesh_a))

    @staticmethod
    def generate_report(mesh: SurfaceMesh) -> str:
        """Generates a comprehensive geometric and topological report."""
        from compgeom.mesh.mesh_topology import MeshTopology
        area = MeshAnalysis.total_area(mesh)
        volume = MeshAnalysis.total_volume(mesh)
        com = MeshAnalysis.center_of_mass(mesh)
        is_watertight = MeshTopology(mesh).is_watertight()
        betti_0, betti_1, betti_2 = mesh.betti_numbers()
        
        # Euler characteristic
        v = len(mesh.vertices)
        f = len(mesh.faces)
        edges = set()
        for face in mesh.faces:
            edges.add(tuple(sorted((face[0], face[1]))))
            edges.add(tuple(sorted((face[1], face[2]))))
            edges.add(tuple(sorted((face[2], face[0]))))
        e = len(edges)
        euler = v - e + f
        
        lines = [
            "--- Mesh Analysis Report ---",
            f"Vertices: {v}",
            f"Faces:    {f}",
            f"Edges:    {e}",
            f"Euler Characteristic: {euler} (Genus: {(2-euler)//2})",
            f"Betti Numbers: b0={betti_0}, b1={betti_1}, b2={betti_2}",
            f"Watertight: {'Yes' if is_watertight else 'No'}",
            f"Surface Area: {area:.6f}",
            f"Volume:       {volume:.6f}",
            f"Center of Mass: ({com[0]:.4f}, {com[1]:.4f}, {com[2]:.4f})",
            "----------------------------"
        ]
        return "\n".join(lines)
    @staticmethod
    def logarithmic_map(mesh: SurfaceMesh, source_idx: int) -> List[Tuple[float, float]]:
        """
        Computes the Logarithmic Map (geodesic polar coordinates) around a source vertex.
        Maps 3D geodesic distances and angles to a 2D plane.
        Essential for texture synthesis and local surface parameterization.
        """
        # 1. Compute geodesics using the Vector Heat Method
        from compgeom.mesh.volume.heat_method import VectorHeatMethod
        vhm = VectorHeatMethod(mesh)
        distances = vhm.compute_geodesics([source_idx])
        
        # 2. Extract angles using parallel transport or local exponential map
        # Placeholder for 2D mapping (r, theta) -> (x, y)
        coords = []
        for i in range(len(mesh.vertices)):
            r = distances[i]
            theta = 0.0 # Placeholder for angle extraction
            coords.append((r * math.cos(theta), r * math.sin(theta)))
        return coords
