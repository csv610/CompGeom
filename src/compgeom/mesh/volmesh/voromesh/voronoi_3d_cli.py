from __future__ import annotations
import argparse
import random
import sys
import os

# Ensure local imports work if run as a script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from compgeom.kernel import Point3D
from compgeom.mesh.volmesh.voronoi_3d import VoronoiDiagram3D
from compgeom.mesh.volmesh.bounded_voronoi_3d import BoundedVoronoi3D

def demo_points_3d(n: int = 10, size: float = 100.0) -> list[Point3D]:
    random.seed(42)
    return [Point3D(random.uniform(0, size), 
                    random.uniform(0, size), 
                    random.uniform(0, size), i) for i in range(n)]

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a 3D Voronoi diagram.")
    parser.add_argument("--num-points", type=int, default=10, help="Number of random points to generate.")
    parser.add_argument("--boundary", choices=["none", "box", "sphere", "cylinder"], default="box", help="Boundary type.")
    parser.add_argument("--size", type=float, default=100.0, help="Size of the bounding box/sphere/cylinder.")
    parser.add_argument("--visualize", action="store_true", help="Visualize using PyVista (requires pyvista).")
    
    args = parser.parse_args(argv)
    
    points = demo_points_3d(args.num_points, args.size)
    print(f"Generated {len(points)} points.")
    
    if args.boundary == "none":
        voronoi = VoronoiDiagram3D()
        mesh = voronoi.compute(points)
        print("Computed unbounded 3D Voronoi diagram.")
    elif args.boundary == "box":
        bv = BoundedVoronoi3D.from_box(Point3D(0, 0, 0), Point3D(args.size, args.size, args.size))
        mesh = bv.compute(points)
        print(f"Computed box-bounded 3D Voronoi diagram (0 to {args.size}).")
    elif args.boundary == "sphere":
        bv = BoundedVoronoi3D.from_sphere(Point3D(args.size/2, args.size/2, args.size/2), args.size/2)
        mesh = bv.compute(points)
        print(f"Computed sphere-bounded 3D Voronoi diagram (radius {args.size/2}).")
    elif args.boundary == "cylinder":
        bv = BoundedVoronoi3D.from_cylinder(Point3D(args.size/2, args.size/2, args.size/2), args.size/2, args.size)
        mesh = bv.compute(points)
        print(f"Computed cylinder-bounded 3D Voronoi diagram.")

    print(f"Result: {len(mesh.vertices)} Voronoi vertices, {len(mesh.poly_cells)} cells.")
    
    if args.visualize:
        try:
            import pyvista as pv
            import numpy as np
            
            plotter = pv.Plotter()
            # Add seed points
            seeds = np.array([[p.x, p.y, p.z] for p in points])
            plotter.add_points(seeds, color="red", point_size=10, render_points_as_spheres=True)
            
            # Add Voronoi cells
            v_coords = np.array([[v.x, v.y, v.z] for v in mesh.vertices])
            for cell_faces in mesh.poly_cells:
                if not cell_faces: continue
                # We can represent each cell as a PolyData
                pv_faces = []
                for face in cell_faces:
                    pv_faces.append(len(face))
                    pv_faces.extend(face)
                
                if pv_faces:
                    cell_mesh = pv.PolyData(v_coords, pv_faces)
                    plotter.add_mesh(cell_mesh, show_edges=True, opacity=0.3, 
                                     color=random.sample(range(256), 3))
            
            plotter.show()
        except ImportError:
            print("Error: pyvista not found. Visualization skipped.")
            return 1
        except Exception as e:
            print(f"Error during visualization: {e}")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
