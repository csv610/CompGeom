from __future__ import annotations

import argparse
import sys
import math
import numpy as np
from compgeom.mesh import MeshImporter
from compgeom.mesh.mesh_geometry import MeshGeometry
from compgeom.point.sphere_sampling import SphereSampler
from compgeom.kernel import Point3D


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sample SO3/Sphere space around a mesh to create canonical (vintage) views using HEALPix."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input mesh file."
    )
    parser.add_argument(
        "-n", "--nside", type=int, default=1, help="HEALPix Nside parameter (default: 1, gives 12 views)."
    )
    parser.add_argument(
        "-d", "--distance", type=float, default=2.0, help="Camera distance multiplier relative to mesh radius (default: 2.0)."
    )
    parser.add_argument(
        "-o", "--output", help="Path to output text file for camera positions."
    )
    parser.add_argument(
        "--so3", type=int, help="Number of SO(3) rotations to sample (ignores nside if provided)."
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Visualize viewpoints and mesh using PyVista."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    # 1. Compute mesh center and scale
    center = MeshGeometry.centroid(mesh)
    bbox = MeshGeometry.bounding_box(mesh)
    if not bbox:
        print("Error: Empty mesh.")
        return 1
    
    bmin, bmax = bbox
    diag = math.sqrt(sum((bmax[i] - bmin[i])**2 for i in range(len(bmin))))
    radius = diag * 0.5
    cam_dist = radius * args.distance

    print(f"Mesh radius: {radius:.4f}, Camera distance: {cam_dist:.4f}")

    # 2. Sample Space
    viewpoints = []
    quaternions = []
    
    if args.so3:
        print(f"Sampling {args.so3} full SO(3) rotations (Quaternions)...")
        quaternions = SphereSampler.sample_so3(args.so3)
        # For visualization, we treat camera as being at (0,0,dist) rotated by q
        for q in quaternions:
            mat = SphereSampler.quaternion_to_matrix(q)
            # Default camera position at +Z axis
            pos = mat @ np.array([0, 0, cam_dist])
            viewpoints.append(Point3D(center.x + pos[0], center.y + pos[1], getattr(center, 'z', 0.0) + pos[2]))
    else:
        print(f"Sampling {12 * args.nside**2} viewpoints using HEALPix...")
        sphere_points = SphereSampler.healpix_sampling(n_side=args.nside)
        for p in sphere_points:
            viewpoints.append(Point3D(
                center.x + p.x * cam_dist,
                center.y + p.y * cam_dist,
                getattr(center, 'z', 0.0) + p.z * cam_dist
            ))

    # 4. Output
    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(f"# Target Centroid: {center.x:.6f} {center.y:.6f} {getattr(center, 'z', 0.0):.6f}\n")
                if quaternions:
                    f.write("# Rotation Quaternions (w, x, y, z)\n")
                    for q in quaternions:
                        f.write(f"{q[0]:.8f} {q[1]:.8f} {q[2]:.8f} {q[3]:.8f}\n")
                else:
                    f.write("# Viewpoint (Camera Position) x, y, z\n")
                    for v in viewpoints:
                        f.write(f"{v.x:.8f} {v.y:.8f} {v.z:.8f}\n")
            print(f"Results written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}")
            return 1
    else:
        if quaternions:
            for i, q in enumerate(quaternions):
                print(f"Rotation {i:2}: Quat(w={q[0]:.4f}, x={q[1]:.4f}, y={q[2]:.4f}, z={q[3]:.4f})")
        else:
            for i, v in enumerate(viewpoints):
                print(f"View {i:2}: Pos({v.x:8.4f}, {v.y:8.4f}, {v.z:8.4f})")

    # 5. Optional visualization
    if args.visualize:
        try:
            import pyvista as pv
            plotter = pv.Plotter()
            
            # Add mesh
            v_arr = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
            f_arr = []
            for face in mesh.faces:
                f_arr.append(len(face))
                f_arr.extend(face.v_indices)
            
            pv_mesh = pv.PolyData(v_arr, np.array(f_arr))
            plotter.add_mesh(pv_mesh, color="lightblue", opacity=0.7, show_edges=True)
            
            # Add viewpoints as points
            vp_arr = np.array([[v.x, v.y, v.z] for v in viewpoints])
            plotter.add_points(vp_arr, color="red", point_size=10, render_points_as_spheres=True)
            
            # Add lines from viewpoints to center
            c_arr = np.array([center.x, center.y, getattr(center, 'z', 0.0)])
            for vp in vp_arr:
                plotter.add_lines(np.vstack([vp, c_arr]), color="gray", width=1)
                
            plotter.add_axes()
            plotter.show()
        except ImportError:
            print("Error: PyVista not installed. Visualization skipped.")
        except Exception as e:
            print(f"Error during visualization: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
