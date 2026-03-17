from __future__ import annotations

import argparse
import sys

from compgeom import euler_characteristic
from compgeom.mesh import MeshImporter, OBJFileHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute Euler characteristic for a mesh.")
    parser.add_argument("input_file", help="Input mesh file (OBJ, OFF, STL, PLY).")
    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input_file)
        vertices, faces = mesh.vertices, mesh.elements
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1

    # Ensure all faces are triangles for euler_characteristic function
    from compgeom.mesh.mesh import PolygonMesh
    if isinstance(mesh, PolygonMesh):
        mesh = mesh.triangulate()
    vertices, faces = mesh.vertices, mesh.elements
    tri_indices = faces
    triangles = [tuple(vertices[i] for i in face) for face in tri_indices]

    if not triangles:
        print("Error: No triangles found in input mesh.")
        return 1

    result = euler_characteristic(triangles)
    print("Mesh Topology:")
    print(f"  Vertices: {result['vertices']}")
    print(f"  Edges:    {result['edges']}")
    print(f"  Faces:    {result['faces']}")
    print(f"  Euler characteristic: {result['euler_characteristic']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
