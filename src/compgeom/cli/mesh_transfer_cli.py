import argparse
import sys
import math
from compgeom import Point2D
from compgeom import TriangleMesh, MeshTransfer, OBJFileHandler

def main():
    parser = argparse.ArgumentParser(description="Transfer mesh topology to a new polygonal domain.")
    parser.add_argument("--input", required=True, help="Input source OBJ file")
    parser.add_argument("--target", nargs="+", help="Target polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--output", required=True, help="Output OBJ file")
    
    args = parser.parse_args()
    
    # 1. Load source mesh
    print(f"Reading source mesh from {args.input}...")
    source_mesh = TriangleMesh.from_file(args.input)
    print(f"Source: {len(source_mesh.vertices)} vertices, {len(source_mesh.faces)} triangles.")
    
    # 2. Define target polygon
    if args.target:
        try:
            raw = [float(x) for x in args.target]
            target_poly = [Point2D(raw[i], raw[i+1]) for i in range(0, len(raw), 2)]
        except Exception as e:
            print(f"Error parsing target polygon: {e}")
            sys.exit(1)
    else:
        # Default: transform unit square to a unit circle
        print("No target provided. Defaulting to unit circle domain.")
        n_segments = 64
        target_poly = []
        for i in range(n_segments):
            theta = 2.0 * math.pi * i / n_segments
            target_poly.append(Point2D(0.5 + 0.5 * math.cos(theta), 0.5 + 0.5 * math.sin(theta)))
            
    # 3. Perform transfer
    print("Transferring triangulation...")
    try:
        new_mesh = MeshTransfer.transfer(source_mesh, target_poly)
        print(f"Successfully transferred to new domain.")
    except Exception as e:
        print(f"Transfer failed: {e}")
        sys.exit(1)
        
    # 4. Save result
    print(f"Writing result to {args.output}...")
    OBJFileHandler.write(args.output, new_mesh)
    print("Done.")

if __name__ == "__main__":
    main()
