from __future__ import annotations

import argparse
import numpy as np
from compgeom.mesh import meshio, OBJFileHandler
from compgeom.mesh.volume.tetmesh.robust_mesher import RobustTetMesher

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a constrained tetrahedral mesh from a surface mesh.")
    parser.add_argument("input", help="Path to input surface mesh file (OBJ, OFF, etc.).")
    parser.add_argument("output", help="Path to output tetrahedral mesh file (OBJ/OFF only support faces, but here we save as .obj with cells).")
    parser.add_argument("--refine", type=float, default=1.0, help="Refinement factor for internal Steiner points.")
    
    args = parser.parse_args(argv)
    
    print(f"Reading surface mesh from {args.input}...")
    try:
        mesh = meshio.from_file(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1
        
    # RobustTetMesher expects numpy arrays
    vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
    faces = np.array([f.v_indices for f in mesh.faces])
    
    print(f"Generating tetrahedral mesh (refinement={args.refine})...")
    mesher = RobustTetMesher(vertices, faces)
    tet_mesh = mesher.mesh(refinement_factor=args.refine)
    
    print(f"Tetrahedralization complete: {len(tet_mesh.vertices)} vertices, {len(tet_mesh.cells)} tetrahedra.")
    
    print(f"Writing result to {args.output}...")
    try:
        # Note: standard OBJ/OFF don't support tets directly, 
        # but our meshio handlers can write them as cell vertex indices.
        meshio.to_file(args.output, tet_mesh)
        print("Done.")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
