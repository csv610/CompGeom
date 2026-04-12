from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.mesh.surface.mesh_decimation import MeshDecimator
from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reduce the number of faces in a triangle mesh using QEM decimation."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input triangle mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output mesh file."
    )
    parser.add_argument(
        "-f", "--faces", type=int, required=True, help="Target number of faces after decimation."
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
                print("Error: Could not triangulate mesh.")
                return 1
        except Exception as e:
            print(f"Error during triangulation: {e}")
            return 1

    print(f"Decimating mesh to {args.faces} faces...")
    
    try:
        decimated_mesh = MeshDecimator.decimate(mesh, target_faces=args.faces)
    except Exception as e:
        print(f"Error during decimation: {e}")
        return 1

    try:
        MeshExporter.write(args.output, decimated_mesh)
        print(f"Decimated mesh written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
