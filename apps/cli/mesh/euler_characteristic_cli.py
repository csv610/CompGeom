from __future__ import annotations

import argparse
from compgeom.mesh import from_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute Euler characteristic for a mesh."
    )
    parser.add_argument("input_file", help="Input mesh file (OBJ, OFF, STL, PLY).")
    args = parser.parse_args(argv)

    try:
        mesh = from_file(args.input_file)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1

    v = len(mesh.vertices)
    e = mesh.num_edges if hasattr(mesh, "num_edges") else 0
    f = len(mesh.elements)

    result = (
        mesh.euler_characteristic()
        if hasattr(mesh, "euler_characteristic")
        else v - e + f
    )

    print("Mesh Topology:")
    print(f"  Vertices: {v}")
    print(f"  Edges:    {e}")
    print(f"  Faces:    {f}")
    print(f"  Euler characteristic: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
