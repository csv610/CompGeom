from __future__ import annotations

import argparse
from compgeom import Point2D, TriMesh, MeshTransfer, OBJFileHandler

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Transfer mesh topology to a new polygonal domain.")
    parser.add_argument("--input", required=True, help="Input source OBJ file.")
    parser.add_argument("--target", nargs="+", required=True, help="Target polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--output", required=True, help="Output OBJ file")
    
    args = parser.parse_args(argv)
    
    # 1. Load source mesh
    print(f"Reading source mesh from {args.input}...")
    try:
        source_mesh = TriMesh.from_file(args.input)
    except Exception as e:
        print(f"Error reading source mesh: {e}")
        return 1
        
    print(f"Source: {len(source_mesh.vertices)} vertices, {len(source_mesh.faces)} triangles.")
    
    # 2. Define target polygon
    try:
        raw = [float(x) for x in args.target]
        if len(raw) % 2 != 0:
            print("Error: Target polygon coordinates must be pairs (x y).")
            return 1
        target_poly = [Point2D(raw[i], raw[i+1]) for i in range(0, len(raw), 2)]
    except Exception as e:
        print(f"Error parsing target polygon: {e}")
        return 1
            
    # 3. Perform transfer
    print("Transferring triangulation...")
    try:
        new_mesh = MeshTransfer.transfer(source_mesh, target_poly)
        print(f"Successfully transferred to new domain.")
    except Exception as e:
        print(f"Transfer failed: {e}")
        return 1
        
    # 4. Save result
    print(f"Writing result to {args.output}...")
    OBJFileHandler.write(args.output, new_mesh)
    print("Done.")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
