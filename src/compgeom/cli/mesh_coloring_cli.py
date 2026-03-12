import argparse
import sys
from compgeom import Point
from compgeom import TriangleMesh, MeshColoring, OBJFileHandler

def main():
    parser = argparse.ArgumentParser(description="Color mesh elements or vertices using a greedy algorithm.")
    parser.add_argument("--input", help="Path to input OBJ file (if not provided, a simple 2D triangulation is used)")
    parser.add_argument("--target", choices=["elements", "vertices"], default="elements", help="What to color (faces/cells or vertices)")
    
    args = parser.parse_args()
    
    if args.input:
        print(f"Reading mesh from {args.input}...")
        mesh = TriangleMesh.from_file(args.input)
    else:
        # Create a simple 2D triangulation: 2 triangles sharing an edge
        vertices = [Point(0,0), Point(1,0), Point(1,1), Point(0,1)]
        faces = [(0, 1, 2), (0, 2, 3)]
        mesh = TriangleMesh(vertices, faces)
        print("Using default simple 2D triangulation (2 triangles).")
        
    print(f"Mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} triangles.")
    
    if args.target == "elements":
        print("Coloring elements (faces)...")
        coloring = MeshColoring.color_elements(mesh)
        label = "Triangle"
    else:
        print("Coloring vertices...")
        coloring = MeshColoring.color_vertices(mesh)
        label = "Vertex"
    
    n_colors = len(set(coloring.values()))
    print(f"\nColoring Results:")
    print(f"  Total Colors Used: {n_colors}")
    
    print(f"\n{label} Index -> Color ID:")
    # Print first 20
    indices = sorted(coloring.keys())
    for i in indices[:20]:
        print(f"  {label} {i:3}: Color {coloring[i]}")
    if len(indices) > 20:
        print(f"  ... and {len(indices)-20} more.") 



    return 0
if __name__ == "__main__":
    main()
