from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.mesh.surface.mesh_processing import MeshProcessing
from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect and fill holes in a triangle mesh."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input triangle mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output mesh file."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    if not isinstance(mesh, TriMesh):
        print("Warning: Input mesh is not a TriMesh. Attempting to triangulate...")
        try:
            if hasattr(mesh, "triangulate"):
                mesh = mesh.triangulate()
            else:
                from compgeom.mesh.surface.polygon.polygon import PolygonMesh
                if isinstance(mesh, PolygonMesh):
                    mesh = mesh.triangulate()
                else:
                    print("Error: Could not triangulate mesh.")
                    return 1
        except Exception as e:
            print(f"Error during triangulation: {e}")
            return 1

    print(f"Detecting and filling holes...")
    
    try:
        fixed_mesh = MeshProcessing.fill_holes(mesh)
        
        # Check if holes were actually filled
        from compgeom.mesh.mesh_topology import MeshTopology
        old_loops = len(MeshTopology(mesh).boundary_loops())
        new_loops = len(MeshTopology(fixed_mesh).boundary_loops())
        
        if old_loops > new_loops:
            print(f"  Successfully filled {old_loops - new_loops} hole(s).")
        else:
            print("  No holes were filled (either no holes found or filling failed).")
            
    except Exception as e:
        print(f"Error during hole filling: {e}")
        return 1

    try:
        MeshExporter.write(args.output, fixed_mesh)
        print(f"Fixed mesh written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
