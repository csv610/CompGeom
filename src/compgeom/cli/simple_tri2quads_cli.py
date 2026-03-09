"""Command-line tool for TriangleMesh to QuadMesh conversion."""

from __future__ import annotations

import argparse
import sys

from compgeom import OBJFileHandler, TriangleMesh, TriangleToQuadConverter

def main():
    parser = argparse.ArgumentParser(description="Convert TriangleMesh to QuadMesh (1-to-3 split).")
    parser.add_argument("input", help="Input OBJ file (TriangleMesh)")
    parser.add_argument("output", help="Output OBJ file (QuadMesh)")
    
    args = parser.parse_args()
    
    print(f"Reading triangle mesh from {args.input}...")
    try:
        vertices, faces = OBJFileHandler.read(args.input)
        # Ensure input is triangulated
        tri_faces = OBJFileHandler.triangulate_faces(faces)
        tri_mesh = TriangleMesh(vertices, tri_faces)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    print(f"Initial: {len(tri_mesh.vertices)} vertices, {len(tri_mesh.faces)} triangles.")
    
    quad_mesh = TriangleToQuadConverter.convert(tri_mesh)
    
    print(f"Converted: {len(quad_mesh.vertices)} vertices, {len(quad_mesh.faces)} quads.")
    
    print(f"Writing quad mesh to {args.output}...")
    OBJFileHandler.write(args.output, quad_mesh.vertices, quad_mesh.faces)
    print("Done.")


if __name__ == "__main__":
    main()
