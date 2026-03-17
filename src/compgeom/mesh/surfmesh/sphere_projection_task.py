
import math
import numpy as np
from collections import defaultdict
from typing import List, Tuple

# Assuming these are available in the environment
from compgeom.mesh import TriangleMesh
from compgeom.kernel import Point3D
from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
from compgeom.mesh.surfmesh.mesh_processing import MeshProcessing
from compgeom.mesh.surfmesh.mesh_validation import MeshValidation
from compgeom.mesh.surfmesh.trimesh.primitives import Primitives

def calculate_sphere_radius(area: float) -> float:
    """Find the radius of the sphere with the same area: A = 4 * pi * r^2."""
    return math.sqrt(area / (4 * math.pi))

def project_to_sphere(mesh: TriangleMesh, center: Tuple[float, float, float], radius: float) -> TriangleMesh:
    """Project the points on the sphere with same topology."""
    new_vertices = []
    for v in mesh.vertices:
        vx, vy, vz = v.x - center[0], v.y - center[1], getattr(v, 'z', 0.0) - center[2]
        dist = math.sqrt(vx*vx + vy*vy + vz*vz)
        if dist < 1e-12:
            # Should not happen if mesh is not a point
            new_vertices.append(Point3D(center[0] + radius, center[1], center[2]))
            continue
        scale = radius / dist
        new_vertices.append(Point3D(center[0] + vx * scale, center[1] + vy * scale, center[2] + vz * scale))
    
    return TriangleMesh(new_vertices, mesh.faces)

def is_mesh_valid_on_sphere(mesh: TriangleMesh, center: Tuple[float, float, float], verbose=False) -> bool:
    """
    Check if all elements are valid:
    1. No degenerate faces (area > 1e-9).
    2. All faces are oriented outwards (normal dot radial vector > 0).
    """
    normals = MeshAnalysis.compute_face_normals(mesh)
    invalid_count = 0
    degenerate_count = 0
    flipped_count = 0
    
    for i, face in enumerate(mesh.faces):
        # 1. Check for degeneracy
        if normals[i] == (0.0, 0.0, 0.0):
            degenerate_count += 1
            invalid_count += 1
            continue
        
        # 2. Check orientation
        v0, v1, v2 = [mesh.vertices[idx] for idx in face]
        cx = (v0.x + v1.x + v2.x) / 3.0
        cy = (v0.y + v1.y + v2.y) / 3.0
        cz = (getattr(v0, 'z', 0.0) + getattr(v1, 'z', 0.0) + getattr(v2, 'z', 0.0)) / 3.0
        
        radial_vec = (cx - center[0], cy - center[1], cz - center[2])
        dot = normals[i][0] * radial_vec[0] + normals[i][1] * radial_vec[1] + normals[i][2] * radial_vec[2]
        
        if dot <= 0: # More lenient check
            flipped_count += 1
            invalid_count += 1
            
    if verbose and invalid_count > 0:
        print(f"Validity Check: {invalid_count} invalid faces ({degenerate_count} degenerate, {flipped_count} flipped).")
            
    return invalid_count == 0

def apply_spherical_smoothing(mesh: TriangleMesh, center: Tuple[float, float, float], radius: float, max_iterations: int = 100) -> TriangleMesh:
    """Apply smoothing on the spherical mesh till all elements are valid, fixing the first triangle."""
    
    # Vertices to fix (first triangle)
    fixed_indices = set(mesh.faces[0]) if mesh.faces else set()

    # Precompute adjacency
    adj = defaultdict(set)
    for face in mesh.faces:
        for i in range(3):
            u, v = face[i], face[(i+1)%3]
            adj[u].add(v)
            adj[v].add(u)
            
    current_mesh = mesh
    for i in range(max_iterations):
        if is_mesh_valid_on_sphere(current_mesh, center, verbose=(i % 10 == 0)):
            print(f"Mesh became valid after {i} iterations.")
            return current_mesh
            
        # Perform one step of Laplacian smoothing and project back
        new_vertices = []
        for j, v in enumerate(current_mesh.vertices):
            if j in fixed_indices:
                new_vertices.append(v)
                continue

            neighbors = adj[j]
            if not neighbors:
                new_vertices.append(v)
                continue
            
            sum_x = sum_y = sum_z = 0.0
            for nb_idx in neighbors:
                nb = current_mesh.vertices[nb_idx]
                sum_x += nb.x
                sum_y += nb.y
                sum_z += getattr(nb, 'z', 0.0)
            
            # Laplacian step (lambda=0.5)
            avg_x = sum_x / len(neighbors)
            avg_y = sum_y / len(neighbors)
            avg_z = sum_z / len(neighbors)
            
            vx = 0.5 * v.x + 0.5 * avg_x
            vy = 0.5 * v.y + 0.5 * avg_y
            vz = 0.5 * getattr(v, 'z', 0.0) + 0.5 * avg_z
            
            # Project back to sphere
            dx, dy, dz = vx - center[0], vy - center[1], vz - center[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist > 1e-12:
                scale = radius / dist
                new_vertices.append(Point3D(center[0] + dx * scale, center[1] + dy * scale, center[2] + dz * scale))
            else:
                new_vertices.append(v)
                
        current_mesh = TriangleMesh(new_vertices, current_mesh.faces)
        
    is_mesh_valid_on_sphere(current_mesh, center, verbose=True)
    print(f"Warning: Reached max iterations ({max_iterations}) and mesh is still not fully valid.")
    return current_mesh


def as_rigid_as_possible(mesh: TriangleMesh, original_mesh: TriangleMesh, center: Tuple[float, float, float], radius: float, iterations: int = 50, step_size: float = 0.5) -> TriangleMesh:
    """
    Optimizes the spherical mesh so that edge lengths are approximately equal 
    to those in the original mesh (As-Rigid-As-Possible), fixing the first triangle.
    """
    # Vertices to fix (first triangle)
    fixed_indices = set(mesh.faces[0]) if mesh.faces else set()

    # 1. Precompute original edge lengths
    original_lengths = {}
    adj = defaultdict(set)
    for face in original_mesh.faces:
        for i in range(3):
            u, v = sorted((face[i], face[(i+1)%3]))
            if (u, v) not in original_lengths:
                v_u, v_v = original_mesh.vertices[u], original_mesh.vertices[v]
                dist = math.sqrt((v_u.x - v_v.x)**2 + (v_u.y - v_v.y)**2 + (getattr(v_u, 'z', 0.0) - getattr(v_v, 'z', 0.0))**2)
                original_lengths[(u, v)] = dist
            adj[u].add(v)
            adj[v].add(u)

    current_vertices = [Point3D(v.x, v.y, getattr(v, 'z', 0.0)) for v in mesh.vertices]
    
    for _ in range(iterations):
        temp_vertices = []
        for i, v in enumerate(current_vertices):
            if i in fixed_indices:
                temp_vertices.append(v)
                continue

            sum_target = [0.0, 0.0, 0.0]
            neighbors = adj[i]
            if not neighbors:
                temp_vertices.append(v)
                continue
            
            for nb_idx in neighbors:
                nb = current_vertices[nb_idx]
                L_ij = original_lengths[tuple(sorted((i, nb_idx)))]
                
                # Desired vector from nb to i has length L_ij
                dx, dy, dz = v.x - nb.x, v.y - nb.y, getattr(v, 'z', 0.0) - getattr(nb, 'z', 0.0)
                curr_dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if curr_dist > 1e-12:
                    scale = L_ij / curr_dist
                    sum_target[0] += nb.x + dx * scale
                    sum_target[1] += nb.y + dy * scale
                    sum_target[2] += getattr(nb, 'z', 0.0) + dz * scale
                else:
                    sum_target[0] += v.x
                    sum_target[1] += v.y
                    sum_target[2] += getattr(v, 'z', 0.0)
            
            avg_target = [s / len(neighbors) for s in sum_target]
            
            # Step towards target
            nx = v.x + step_size * (avg_target[0] - v.x)
            ny = v.y + step_size * (avg_target[1] - v.y)
            nz = getattr(v, 'z', 0.0) + step_size * (avg_target[2] - getattr(v, 'z', 0.0))
            
            # Project back to sphere
            dx, dy, dz = nx - center[0], ny - center[1], nz - center[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist > 1e-12:
                scale = radius / dist
                temp_vertices.append(Point3D(center[0] + dx * scale, center[1] + dy * scale, center[2] + dz * scale))
            else:
                temp_vertices.append(v)
        current_vertices = temp_vertices

    return TriangleMesh(current_vertices, mesh.faces)

def as_conformal_as_possible(mesh: TriangleMesh, original_mesh: TriangleMesh, center: Tuple[float, float, float], radius: float, iterations: int = 50, step_size: float = 0.5) -> TriangleMesh:
    """
    Optimizes the spherical mesh to preserve triangle shapes (angles) 
    using cotangent weights from the original mesh, fixing the first triangle.
    """
    # Vertices to fix (first triangle)
    fixed_indices = set(mesh.faces[0]) if mesh.faces else set()

    # 1. Precompute cotangent weights from original mesh
    weights = defaultdict(float)
    total_weight = defaultdict(float)
    
    for face in original_mesh.faces:
        v_idx = face
        vertices = [original_mesh.vertices[i] for i in v_idx]
        pts = [(v.x, v.y, getattr(v, 'z', 0.0)) for v in vertices]
        
        for i in range(3):
            # i1, i2 are other two vertices
            idx0 = v_idx[i]
            idx1 = v_idx[(i+1)%3]
            idx2 = v_idx[(i+2)%3]
            
            # Vector from idx2 to idx0 and idx2 to idx1
            v_a = (pts[i][0]-pts[(i+2)%3][0], pts[i][1]-pts[(i+2)%3][1], pts[i][2]-pts[(i+2)%3][2])
            v_b = (pts[(i+1)%3][0]-pts[(i+2)%3][0], pts[(i+1)%3][1]-pts[(i+2)%3][1], pts[(i+1)%3][2]-pts[(i+2)%3][2])
            
            # Area * 2
            cross_x = v_a[1]*v_b[2] - v_a[2]*v_b[1]
            cross_y = v_a[2]*v_b[0] - v_a[0]*v_b[2]
            cross_z = v_a[0]*v_b[1] - v_a[1]*v_b[0]
            area2 = math.sqrt(cross_x**2 + cross_y**2 + cross_z**2)
            
            dot = v_a[0]*v_b[0] + v_a[1]*v_b[1] + v_a[2]*v_b[2]
            
            cot = dot / area2 if area2 > 1e-12 else 0.0
            w = 0.5 * cot
            
            u, v = sorted((idx0, idx1))
            weights[(u, v)] += w
            total_weight[idx0] += w
            total_weight[idx1] += w

    adj = defaultdict(set)
    for (u, v) in weights:
        adj[u].add(v)
        adj[v].add(u)

    current_vertices = [Point3D(v.x, v.y, getattr(v, 'z', 0.0)) for v in mesh.vertices]
    
    for _ in range(iterations):
        temp_vertices = []
        for i, v in enumerate(current_vertices):
            if i in fixed_indices:
                temp_vertices.append(v)
                continue

            neighbors = adj[i]
            if not neighbors or total_weight[i] == 0:
                temp_vertices.append(v)
                continue
            
            sum_w_nb = [0.0, 0.0, 0.0]
            for nb_idx in neighbors:
                w = weights[tuple(sorted((i, nb_idx)))]
                nb = current_vertices[nb_idx]
                sum_w_nb[0] += w * nb.x
                sum_w_nb[1] += w * nb.y
                sum_w_nb[2] += w * getattr(nb, 'z', 0.0)
            
            avg_x = sum_w_nb[0] / total_weight[i]
            avg_y = sum_w_nb[1] / total_weight[i]
            avg_z = sum_w_nb[2] / total_weight[i]
            
            # Step towards weighted average
            nx = v.x + step_size * (avg_x - v.x)
            ny = v.y + step_size * (avg_y - v.y)
            nz = getattr(v, 'z', 0.0) + step_size * (avg_z - getattr(v, 'z', 0.0))
            
            # Project back to sphere
            dx, dy, dz = nx - center[0], ny - center[1], nz - center[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist > 1e-12:
                scale = radius / dist
                temp_vertices.append(Point3D(center[0] + dx * scale, center[1] + dy * scale, center[2] + dz * scale))
            else:
                temp_vertices.append(v)
        current_vertices = temp_vertices

    return TriangleMesh(current_vertices, mesh.faces)


def main():
    # 0. Setup an input mesh (e.g. an ellipsoid)
    print("Creating input mesh (ellipsoid)...")
    original_mesh = Primitives.ellipsoid(rx=2.0, ry=1.0, rz=1.0, subdivisions=3)
    
    # Fix orientation (PlatonicSolid.icosahedron is CW, we want CCW)
    com = MeshAnalysis.center_of_mass(original_mesh)
    new_faces = [(f[0], f[2], f[1]) for f in original_mesh.faces]
    original_mesh = TriangleMesh(original_mesh.vertices, new_faces)
    
    # 1. Calculate surface area
    area = MeshAnalysis.total_area(original_mesh)
    print(f"Total Surface Area: {area:.6f}")
    
    # 2. Find radius of sphere with same area
    radius = calculate_sphere_radius(area)
    print(f"Equivalent Sphere Radius: {radius:.6f}")
    
    # 3. Project the points on the sphere
    print(f"Center of Mass: {com}")
    print("Projecting vertices to sphere...")
    spherical_mesh = project_to_sphere(original_mesh, com, radius)
    
    # 5. Apply smoothing on the spherical mesh till all elements are valid
    print("Applying initial spherical smoothing...")
    smoothed_mesh = apply_spherical_smoothing(spherical_mesh, com, radius)
    
    # 6. ARAP Optimization
    print("Applying As-Rigid-As-Possible optimization...")
    arap_mesh = as_rigid_as_possible(smoothed_mesh, original_mesh, com, radius, iterations=100, step_size=0.1)
    
    # 7. ACAP Optimization
    print("Applying As-Conformal-As-Possible optimization...")
    acap_mesh = as_conformal_as_possible(smoothed_mesh, original_mesh, com, radius, iterations=100, step_size=0.1)
    
    # Final check
    print("Final ARAP Validity Check:")
    arap_valid = is_mesh_valid_on_sphere(arap_mesh, com, verbose=True)
    print(f"ARAP Result: {'Passed' if arap_valid else 'Failed'}")
    
    print("\nFinal ACAP Validity Check:")
    acap_valid = is_mesh_valid_on_sphere(acap_mesh, com, verbose=True)
    print(f"ACAP Result: {'Passed' if acap_valid else 'Failed'}")
    
    print(f"Process complete.")

if __name__ == "__main__":
    main()

