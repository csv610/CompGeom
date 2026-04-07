from __future__ import annotations

import argparse
from compgeom.mesh import meshio

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert between different 3D mesh formats (OBJ, OFF, STL, PLY).")
    parser.add_argument("input", help="Input mesh file path.")
    parser.add_argument("output", help="Output mesh file path.")
    parser.add_argument("--binary", action="store_true", help="Write binary format if supported (STL, PLY).")
    
    args = parser.parse_args(argv)
    
    print(f"Reading mesh from {args.input}...")
    try:
        mesh = meshio.from_file(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1
        
    print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.elements)} elements.")
    
    print(f"Writing mesh to {args.output}...")
    try:
        # Pass binary flag for formats that support it
        kwargs = {}
        if args.binary:
            kwargs['binary'] = True
            
        meshio.to_file(args.output, mesh, **kwargs)
        print("Conversion successful.")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
