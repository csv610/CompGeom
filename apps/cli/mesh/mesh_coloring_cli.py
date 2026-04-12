from __future__ import annotations

import argparse

from compgeom.mesh.meshio import MeshImporter
from compgeom.mesh.algorithms.mesh_coloring import MeshColoring


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Color mesh elements or vertices using a greedy algorithm."
    )
    parser.add_argument("input", help="Path to input mesh file")
    parser.add_argument(
        "--target",
        choices=["elements", "vertices"],
        default="elements",
        help="What to color (faces/cells or vertices)",
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1

    print(f"Mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces.")

    if args.target == "elements":
        print("Coloring elements (faces)...")
        coloring = MeshColoring.color_elements(mesh)
        label = "Face"
    else:
        print("Coloring vertices...")
        coloring = MeshColoring.color_vertices(mesh)
        label = "Vertex"

    n_colors = len(set(coloring.values()))
    print(f"Coloring Results:")
    print(f"  Total Colors Used: {n_colors}")

    indices = sorted(coloring.keys())
    for i in indices[:20]:
        print(f"  {label} {i:3}: Color {coloring[i]}")
    if len(indices) > 20:
        print(f"  ... and {len(indices) - 20} more.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
