import argparse
import sys
from compgeom.geometry import Point
from compgeom.mesh import TriangleMesh, OBJFileHandler

def main():
    parser = argparse.ArgumentParser(description="Refine a triangular mesh.")
    parser.add_argument("--input", help="Path to input OBJ file (if not provided, a single 2D triangle is used)")
    parser.add_argument("--iterations", type=int, default=1, help="Number of linear subdivision iterations")
    parser.add_argument("--max_area", type=float, help="Maximum triangle area as ratio of total area (e.g. 0.01 for 1%%)")
    parser.add_argument("--output", help="Path to output OBJ file")
    
    args = parser.parse_args()
    
    if args.input:
        print(f"Reading mesh from {args.input}...")
        mesh = TriangleMesh.from_file(args.input)
    else:
        # Single triangle with area ~0.433
        vertices = [Point(0,0), Point(1,0), Point(0.5, 0.866)]
        faces = [(0, 1, 2)]
        mesh = TriangleMesh(vertices, faces)
        print("Using default single 2D triangle.")
        
    print(f"Initial Mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} triangles.")
    
    from compgeom.mesh import TriMeshRefiner
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
        OBJFileHandler.write(args.output, refined_mesh.vertices, refined_mesh.faces)
        print(f"Saved refined mesh to {args.output}")

if __name__ == "__main__":
    main()
