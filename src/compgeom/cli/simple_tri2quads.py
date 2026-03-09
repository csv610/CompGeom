import argparse
import sys
from compgeom.mesh import TriangleToQuadConverter

def main():
    parser = argparse.ArgumentParser(description="Convert a TriangleMesh to a QuadMesh (1-to-3 split).")
    parser.add_argument("--input", required=True, help="Path to input OBJ file (TriangleMesh)")
    parser.add_argument("--output", required=True, help="Path to output OBJ file (QuadMesh)")
    
    args = parser.parse_args()
    
    # We can invoke the logic directly from the module's main if we want, 
    # but since we exported the class, let's use it.
    from compgeom.mesh import TriangleMesh, OBJFileHandler
    
    print(f"Reading mesh from {args.input}...")
    vertices, faces = OBJFileHandler.read(args.input)
    # Ensure it is triangulated for conversion
    faces = OBJFileHandler.triangulate_faces(faces)
    tri_mesh = TriangleMesh(vertices, faces)
    
    print(f"Converting {len(tri_mesh.faces)} triangles to quads...")
    quad_mesh = TriangleToQuadConverter.convert(tri_mesh)
    
    print(f"Generated {len(quad_mesh.faces)} quads.")
    print(f"Writing to {args.output}...")
    OBJFileHandler.write(args.output, quad_mesh.vertices, quad_mesh.faces)
    print("Done.")

if __name__ == "__main__":
    main()
