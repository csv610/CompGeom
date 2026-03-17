
import math
import numpy as np
from collections import defaultdict
from typing import List, Tuple

from compgeom.mesh import TriangleMesh
from compgeom.kernel import Point3D
from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
from compgeom.mesh.surfmesh.trimesh.primitives import Primitives

from sphere_projection_task import (
    calculate_sphere_radius,
    project_to_sphere,
    as_rigid_as_possible,
    as_conformal_as_possible,
    apply_spherical_smoothing
)

def get_edge_lengths(mesh: TriangleMesh) -> dict:
    lengths = {}
    for face in mesh.faces:
        for i in range(3):
            u, v = sorted((face[i], face[(i+1)%3]))
            if (u, v) not in lengths:
                p1, p2 = mesh.vertices[u], mesh.vertices[v]
                d = math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2 + (getattr(p1, 'z', 0.0)-getattr(p2, 'z', 0.0))**2)
                lengths[(u, v)] = d
    return lengths

def get_angles(mesh: TriangleMesh) -> List[float]:
    all_angles = []
    for face in mesh.faces:
        v_idx = face
        pts = [(mesh.vertices[i].x, mesh.vertices[i].y, getattr(mesh.vertices[i], 'z', 0.0)) for i in v_idx]
        for i in range(3):
            p0 = pts[i]
            p1 = pts[(i+1)%3]
            p2 = pts[(i+2)%3]
            v1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
            v2 = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
            m1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
            m2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
            if m1 > 1e-12 and m2 > 1e-12:
                dot = (v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]) / (m1 * m2)
                angle = math.acos(max(-1.0, min(1.0, dot)))
                all_angles.append(angle)
    return all_angles

def calculate_metrics(current_mesh, original_mesh):
    # 1. Edge Length Distortion (L2 norm of relative error)
    curr_lens = get_edge_lengths(current_mesh)
    orig_lens = get_edge_lengths(original_mesh)
    
    errors = []
    for edge, L_orig in orig_lens.items():
        L_curr = curr_lens[edge]
        errors.append(abs(L_curr - L_orig) / L_orig)
    
    avg_edge_error = sum(errors) / len(errors)
    
    # 2. Angle Distortion (Mean absolute difference in radians)
    curr_angles = get_angles(current_mesh)
    orig_angles = get_angles(original_mesh)
    
    angle_diffs = [abs(a - b) for a, b in zip(curr_angles, orig_angles)]
    avg_angle_error = sum(angle_diffs) / len(angle_diffs)
    
    return avg_edge_error, avg_angle_error

def main():
    print("--- Optimization Verification Test ---")
    # Setup
    rx, ry, rz = 2.0, 1.0, 1.0
    orig = Primitives.ellipsoid(rx=rx, ry=ry, rz=rz, subdivisions=2)
    new_faces = [(f[0], f[2], f[1]) for f in orig.faces]
    orig = TriangleMesh(orig.vertices, new_faces)
    
    com = MeshAnalysis.center_of_mass(orig)
    radius = calculate_sphere_radius(MeshAnalysis.total_area(orig))
    
    # Initial State (Naive Projection)
    naive = project_to_sphere(orig, com, radius)
    naive_edge, naive_angle = calculate_metrics(naive, orig)
    
    print(f"Initial (Naive Projection):")
    print(f"  Avg Edge Length Error: {naive_edge:.4%}")
    print(f"  Avg Angle Error:       {math.degrees(naive_angle):.4f} deg")
    
    # Laplacian Smoothing
    smooth = apply_spherical_smoothing(naive, com, radius, max_iterations=20)
    smooth_edge, smooth_angle = calculate_metrics(smooth, orig)
    print(f"\nAfter Laplacian Smoothing:")
    print(f"  Avg Edge Length Error: {smooth_edge:.4%}")
    print(f"  Avg Angle Error:       {math.degrees(smooth_angle):.4f} deg")

    # ARAP Optimization
    arap = as_rigid_as_possible(naive, orig, com, radius, iterations=100, step_size=0.2)
    arap_edge, arap_angle = calculate_metrics(arap, orig)
    print(f"\nAfter ARAP Optimization (Goal: Reduce Edge Error):")
    print(f"  Avg Edge Length Error: {arap_edge:.4%}")
    print(f"  Avg Angle Error:       {math.degrees(arap_angle):.4f} deg")
    print(f"  Edge Improvement:      {(naive_edge - arap_edge)/naive_edge:.2%}")

    # ACAP Optimization
    acap = as_conformal_as_possible(naive, orig, com, radius, iterations=100, step_size=0.2)
    acap_edge, acap_angle = calculate_metrics(acap, orig)
    print(f"\nAfter ACAP Optimization (Goal: Reduce Angle Error):")
    print(f"  Avg Edge Length Error: {acap_edge:.4%}")
    print(f"  Avg Angle Error:       {math.degrees(acap_angle):.4f} deg")
    print(f"  Angle Improvement:     {(naive_angle - acap_angle)/naive_angle:.2%}")

if __name__ == "__main__":
    main()
