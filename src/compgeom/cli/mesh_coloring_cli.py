from __future__ import annotations

import argparse
from compgeom import TriMesh, MeshColoring

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Color mesh elements or vertices using a greedy algorithm.")
    parser.add_argument("--input", required=True, help="Path to input OBJ file.")
    parser.add_argument("--target", choices=["elements", "vertices"], default="elements", help="What to color (faces/cells or vertices)")
    
    args = parser.parse_args(argv)
    
    print(f"Reading mesh from {args.input}...")
    try:
        mesh = TriMesh.from_file(args.input)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1
        
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
    raise SystemExit(main())
