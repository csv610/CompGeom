import pyvista as pv
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Visualize a 3D mesh using PyVista.")
    parser.add_argument("file", help="Path to the mesh file (e.g., .off, .obj, .stl).")
    parser.add_argument("--edges", action="store_true", help="Show mesh edges.")
    parser.add_argument("--nodes", action="store_true", help="Show mesh nodes (vertices).")
    parser.add_argument("--point-size", type=float, default=5.0, help="Size of the points when --nodes is used.")
    
    args = parser.parse_args()

    try:
        mesh = pv.read(args.file)
    except Exception as e:
        print(f"Error reading file {args.file}: {e}")
        sys.exit(1)

    plotter = pv.Plotter()
    
    # Add the mesh
    plotter.add_mesh(mesh, show_edges=args.edges, color="lightblue", opacity=0.8)
    
    # Add nodes if requested
    if args.nodes:
        plotter.add_points(mesh.points, color="red", point_size=args.point_size, render_points_as_spheres=True)
    
    print("Interactive keys in the viewer:")
    print("  'e' - Toggle edges")
    print("  'v' - Toggle vertices (nodes)")
    print("  'w' - Switch to wireframe")
    print("  's' - Switch to surface")
    print("  'r' - Reset camera")
    print("  'q' - Quit viewer")
    
    plotter.show()

if __name__ == "__main__":
    main()
