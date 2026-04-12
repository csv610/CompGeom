from __future__ import annotations

import argparse

from compgeom import art_gallery_guards
from compgeom.mesh.meshio import MeshImporter
from compgeom.mesh.edge_mesh import EdgeMesh


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Solve the Art Gallery Problem.")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to input OFF file defining the polygon",
    )
    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
        polygon = EdgeMesh(nodes=mesh.vertices, edges=[e.v_indices for e in mesh.edges])
    except Exception as e:
        print(f"Error reading OFF file: {e}")
        return 1

    guards = art_gallery_guards(polygon)

    print(f"Placed {len(guards)} guards (n={len(polygon.nodes)}):")

    for guard in guards:
        print(f"Guard at {guard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
