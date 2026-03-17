"""Sphere Projection Task: Projects a given mesh onto a sphere and optimizes it."""

from __future__ import annotations
import math
import numpy as np
from typing import List, Tuple, Set, Dict

# Standard imports from current project
from .trimesh.trimesh import TriMesh
from ...kernel import Point3D, Sphere
from .mesh_analysis import MeshAnalysis
from .trimesh.primitives import Primitives

class SphereProjector:
    """Handles projection of a mesh onto a sphere and subsequent optimization."""

    def __init__(self, mesh: TriMesh, sphere: Sphere):
        self.original_mesh = mesh
        self.sphere = sphere
        # Cache numpy version of sphere center for efficient vector operations
        self.sphere_center = np.array([sphere.center.x, sphere.center.y, sphere.center.z], dtype=np.float64)
        
        # Fixed vertices (first triangle) to remove rigid body modes
        self.fixed_indices = set(mesh.faces[0]) if mesh.faces else set()
        
        # Use existing topology helper from mesh
        self.topology = mesh.topology
        
        # Current work state
        self.current_vertices = np.array([[v.x, v.y, v.z] for v in mesh.vertices], dtype=np.float64)
        self.faces = np.array(mesh.faces, dtype=np.int32)

    def project_initial(self):
        """Initial projection of all vertices onto the sphere."""
        centered_v = self.current_vertices - self.sphere_center
        dists = np.linalg.norm(centered_v, axis=1)
        # Avoid division by zero
        dists[dists < 1e-12] = 1.0
        scales = self.sphere.radius / dists
        self.current_vertices = self.sphere_center + centered_v * scales[:, np.newaxis]

    def is_valid(self, verbose: bool = False) -> bool:
        """
        Vectorized check for face validity on the sphere:
        1. Non-degenerate area.
        2. Oriented outwards.
        """
        v0 = self.current_vertices[self.faces[:, 0]]
        v1 = self.current_vertices[self.faces[:, 1]]
        v2 = self.current_vertices[self.faces[:, 2]]
        
        # Calculate normals using cross product
        normals = np.cross(v1 - v0, v2 - v0)
        norms = np.linalg.norm(normals, axis=1)
        
        # Filter degenerates
        valid_mask = norms > 1e-12
        degenerate_count = np.sum(~valid_mask)
        
        # Normalize valid normals
        unit_normals = np.zeros_like(normals)
        unit_normals[valid_mask] = normals[valid_mask] / norms[valid_mask][:, np.newaxis]
        
        # Check orientation: (centroid - center) dot normal > 0
        centroids = (v0 + v1 + v2) / 3.0
        radial_vecs = centroids - self.sphere_center
        dots = np.sum(unit_normals * radial_vecs, axis=1)
        
        flipped_count = np.sum(dots[valid_mask] <= 1e-9) # Use small epsilon for robustness
        invalid_count = degenerate_count + flipped_count
        
        if verbose and invalid_count > 0:
            print(f"Validity Check: {invalid_count} invalid faces "
                  f"({degenerate_count} degenerate, {flipped_count} flipped).")
            
        return invalid_count == 0

    def smooth(self, iterations: int = 100, step_size: float = 0.5):
        """Spherical Laplacian smoothing to fix flipped/degenerate triangles."""
        fixed_mask = np.zeros(len(self.current_vertices), dtype=bool)
        for idx in self.fixed_indices:
            fixed_mask[idx] = True
            
        for i in range(iterations):
            if self.is_valid(verbose=(i % 10 == 0)):
                print(f"Mesh became valid after {i} iterations.")
                return
                
            new_verts = self.current_vertices.copy()
            for idx in range(len(self.current_vertices)):
                if fixed_mask[idx]:
                    continue
                
                neighbors = self.topology.vertex_neighbors(idx)
                if not neighbors:
                    continue
                
                # Laplacian step
                avg_neighbor = np.mean(self.current_vertices[list(neighbors)], axis=0)
                new_verts[idx] = (1.0 - step_size) * self.current_vertices[idx] + step_size * avg_neighbor
                
                # Project back to sphere
                dv = new_verts[idx] - self.sphere_center
                dist = np.linalg.norm(dv)
                if dist > 1e-12:
                    new_verts[idx] = self.sphere_center + dv * (self.sphere.radius / dist)
            
            self.current_vertices = new_verts
            
        print(f"Warning: Reached max iterations ({iterations}) and mesh may still be invalid.")

    def optimize_arap(self, iterations: int = 50, step_size: float = 0.5):
        """As-Rigid-As-Possible optimization to preserve edge lengths."""
        # Precompute original edge lengths
        original_lengths = {}
        for f in self.original_mesh.faces:
            for i in range(3):
                u, v = sorted((f[i], f[(i + 1) % 3]))
                if (u, v) not in original_lengths:
                    p_u, p_v = self.original_mesh.vertices[u], self.original_mesh.vertices[v]
                    original_lengths[(u, v)] = math.sqrt((p_u.x - p_v.x)**2 + (p_u.y - p_v.y)**2 + (p_u.z - p_v.z)**2)
        
        fixed_mask = np.zeros(len(self.current_vertices), dtype=bool)
        for idx in self.fixed_indices:
            fixed_mask[idx] = True
            
        for _ in range(iterations):
            new_verts = self.current_vertices.copy()
            for i in range(len(self.current_vertices)):
                if fixed_mask[i]:
                    continue
                
                neighbors = self.topology.vertex_neighbors(i)
                if not neighbors:
                    continue
                
                target_pos = np.zeros(3)
                for nb_idx in neighbors:
                    L_ij = original_lengths[tuple(sorted((i, nb_idx)))]
                    curr_vec = self.current_vertices[i] - self.current_vertices[nb_idx]
                    curr_dist = np.linalg.norm(curr_vec)
                    
                    if curr_dist > 1e-12:
                        # Desired position of vertex i based on neighbor nb_idx
                        target_pos += self.current_vertices[nb_idx] + curr_vec * (L_ij / curr_dist)
                    else:
                        target_pos += self.current_vertices[i]
                
                # Step towards average target
                avg_target = target_pos / len(neighbors)
                update = (1.0 - step_size) * self.current_vertices[i] + step_size * avg_target
                
                # Project back to sphere
                dv = update - self.sphere_center
                dist = np.linalg.norm(dv)
                if dist > 1e-12:
                    new_verts[i] = self.sphere_center + dv * (self.sphere.radius / dist)
                    
            self.current_vertices = new_verts

    def optimize_acap(self, iterations: int = 50, step_size: float = 0.5):
        """As-Conformal-As-Possible optimization using cotangent weights."""
        from collections import defaultdict
        weights = defaultdict(float)
        total_weight = defaultdict(float)
        
        # 1. Precompute cotangent weights from original mesh
        for face in self.original_mesh.faces:
            for i in range(3):
                idx0 = face[i]
                idx1 = face[(i + 1) % 3]
                idx2 = face[(i + 2) % 3]
                
                v0, v1, v2 = [self.original_mesh.vertices[idx] for idx in [idx0, idx1, idx2]]
                p0 = np.array([v0.x, v0.y, v0.z])
                p1 = np.array([v1.x, v1.y, v1.z])
                p2 = np.array([v2.x, v2.y, v2.z])
                
                # Vector from p2 to p0 and p2 to p1
                va = p0 - p2
                vb = p1 - p2
                
                cross_len = np.linalg.norm(np.cross(va, vb))
                dot = np.dot(va, vb)
                
                cot = dot / cross_len if cross_len > 1e-12 else 0.0
                w = 0.5 * cot
                
                u, v = sorted((idx0, idx1))
                weights[(u, v)] += w
                total_weight[idx0] += w
                total_weight[idx1] += w

        fixed_mask = np.zeros(len(self.current_vertices), dtype=bool)
        for idx in self.fixed_indices:
            fixed_mask[idx] = True

        for _ in range(iterations):
            new_verts = self.current_vertices.copy()
            for i in range(len(self.current_vertices)):
                if fixed_mask[i] or total_weight[i] == 0:
                    continue
                
                neighbors = self.topology.vertex_neighbors(i)
                if not neighbors:
                    continue
                
                weighted_sum = np.zeros(3)
                for nb_idx in neighbors:
                    w = weights[tuple(sorted((i, nb_idx)))]
                    weighted_sum += w * self.current_vertices[nb_idx]
                
                avg_pos = weighted_sum / total_weight[i]
                update = (1.0 - step_size) * self.current_vertices[i] + step_size * avg_pos
                
                # Project back
                dv = update - self.sphere_center
                dist = np.linalg.norm(dv)
                if dist > 1e-12:
                    new_verts[i] = self.sphere_center + dv * (self.sphere.radius / dist)
            
            self.current_vertices = new_verts

    def get_mesh(self) -> TriMesh:
        """Returns the current state as a TriMesh object."""
        new_vertices = [Point3D(v[0], v[1], v[2], id=i) for i, v in enumerate(self.current_vertices)]
        return TriMesh(new_vertices, [tuple(f) for f in self.faces])

# --- Wrapper functions for backward compatibility and testing ---

def calculate_sphere_radius(area: float) -> float:
    """Calculates the radius of a sphere with the given surface area."""
    return math.sqrt(area / (4.0 * math.pi))

def project_to_sphere(mesh: TriMesh, center: Tuple[float, float, float] | Point3D, radius: float) -> TriMesh:
    """Projects a mesh onto a sphere defined by center and radius."""
    if isinstance(center, tuple):
        center = Point3D(*center)
    sphere = Sphere(center, radius)
    projector = SphereProjector(mesh, sphere)
    projector.project_initial()
    return projector.get_mesh()

def is_mesh_valid_on_sphere(mesh: TriMesh, center: Tuple[float, float, float] | Point3D) -> bool:
    """Checks if the mesh is validly oriented and non-degenerate on a sphere."""
    if isinstance(center, tuple):
        center = Point3D(*center)
    # Use dummy radius for validity check
    sphere = Sphere(center, 1.0)
    projector = SphereProjector(mesh, sphere)
    return projector.is_valid()

def as_rigid_as_possible(mesh: TriMesh, original_mesh: TriMesh, center: Tuple[float, float, float] | Point3D, radius: float, iterations: int = 50) -> TriMesh:
    """Optimizes a projected mesh using ARAP strategy."""
    if isinstance(center, tuple):
        center = Point3D(*center)
    sphere = Sphere(center, radius)
    projector = SphereProjector(original_mesh, sphere)
    # Start from the current (already projected) state
    projector.current_vertices = np.array([[v.x, v.y, v.z] for v in mesh.vertices], dtype=np.float64)
    projector.optimize_arap(iterations=iterations)
    return projector.get_mesh()

def as_conformal_as_possible(mesh: TriMesh, original_mesh: TriMesh, center: Tuple[float, float, float] | Point3D, radius: float, iterations: int = 50) -> TriMesh:
    """Optimizes a projected mesh using ACAP strategy."""
    if isinstance(center, tuple):
        center = Point3D(*center)
    sphere = Sphere(center, radius)
    projector = SphereProjector(original_mesh, sphere)
    # Start from the current (already projected) state
    projector.current_vertices = np.array([[v.x, v.y, v.z] for v in mesh.vertices], dtype=np.float64)
    projector.optimize_acap(iterations=iterations)
    return projector.get_mesh()


def main():
    # 0. Setup an input mesh (e.g. an ellipsoid)
    print("Creating input mesh (ellipsoid)...")
    original_mesh = Primitives.ellipsoid(rx=2.0, ry=1.0, rz=1.0, subdivisions=3)
    
    # Fix orientation (PlatonicSolid.icosahedron is CW, we want CCW)
    # This is important for outward-pointing normals
    new_faces = [(f[0], f[2], f[1]) for f in original_mesh.faces]
    original_mesh = TriMesh(original_mesh.vertices, new_faces)
    
    # 1. Initialize Sphere and Projector
    area = MeshAnalysis.total_area(original_mesh)
    radius = calculate_sphere_radius(area)
    com = MeshAnalysis.center_of_mass(original_mesh)
    center = Point3D(com[0], com[1], com[2])
    
    sphere = Sphere(center, radius)
    projector = SphereProjector(original_mesh, sphere)
    
    print(f"Surface Area: {area:.6f}")
    print(f"Target Radius: {sphere.radius:.6f}")
    print(f"Center: {sphere.center}")

    # 2. Initial projection
    print("Performing initial projection...")
    projector.project_initial()
    
    # 3. Smoothing
    print("Applying spherical smoothing...")
    projector.smooth(iterations=100, step_size=0.5)
    
    # 4. ARAP
    print("Applying ARAP optimization...")
    projector.optimize_arap(iterations=100, step_size=0.1)
    
    # 5. ACAP
    print("Applying ACAP optimization...")
    projector.optimize_acap(iterations=100, step_size=0.1)
    
    # Final check
    print("\nFinal Validity Check:")
    valid = projector.is_valid(verbose=True)
    print(f"Result: {'Passed' if valid else 'Failed'}")
    
    # Optional: Report final area
    final_mesh = projector.get_mesh()
    final_area = MeshAnalysis.total_area(final_mesh)
    print(f"Final Area: {final_area:.6f} (Diff: {final_area - area:.6f})")

if __name__ == "__main__":
    main()
