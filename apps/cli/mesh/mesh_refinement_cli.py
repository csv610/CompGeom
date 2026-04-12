from __future__ import annotations

import argparse
from compgeom import TriMeshRefiner, TriMesh, OBJFileHandler

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refine a triangular mesh.")
    parser.add_argument("--input", required=True, help="Path to input OBJ file.")
    parser.add_argument("--iterations", type=int, default=1, help="Number of linear subdivision iterations")
    parser.add_argument("--max_area", type=float, help="Maximum triangle area as ratio of total area (e.g. 0.01 for 1%%)")
    parser.add_argument("--output", help="Path to output OBJ file")
    
    args = parser.parse_args(argv)
    
    print(f"Reading mesh from {args.input}...")
    try:
        mesh = TriMesh.from_file(args.input)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1
        
    print(f"Initial Mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} triangles.")
    
    if args.max_area is not None:
        print(f"Refining uniformly until every triangle area <= {args.max_area * 100:.2f}% of total area...")
        refined_mesh = TriMeshRefiner.refine_uniform(mesh, args.max_area)
    else:
        refined_mesh = mesh
        for i in range(args.iterations):
            print(f"Refining linearly (Iteration {i+1})...")
            refined_mesh = TriMeshRefiner.subdivide_linear(refined_mesh)
        
    print(f"\nFinal Mesh: {len(refined_mesh.vertices)} vertices, {len(refined_mesh.faces)} triangles.")
    
    if args.output:
        OBJFileHandler.write(args.output, refined_mesh)
        print(f"Saved refined mesh to {args.output}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
