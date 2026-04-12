from __future__ import annotations

import argparse
import sys
from compgeom.mesh import meshio
from compgeom.mesh.mesh_geometry import MeshGeometry
from compgeom.mesh.mesh_topology import MeshTopology
from compgeom.algo.bounding import minimum_bounding_box
from compgeom.kernel import Point2D, Point3D


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provide detailed information about a 3D or 2D mesh."
    )
    parser.add_argument(
        "input", help="Path to the input mesh file (OBJ, OFF, STL, PLY)."
    )

    args = parser.parse_args(argv)

    print(f"Loading mesh from {args.input}...")
    try:
        mesh = meshio.from_file(args.input)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1

    # Topology
    topo = MeshTopology(mesh)
    n_nodes = mesh.num_nodes()
    n_edges = mesh.num_edges()
    n_faces = mesh.num_faces()
    n_cells = mesh.num_cells()

    n_tri = 0
    n_quad = 0
    n_poly = 0
    if n_faces > 0:
        for face in mesh.faces:
            n_v = len(face)
            if n_v == 3:
                n_tri += 1
            elif n_v == 4:
                n_quad += 1
            else:
                n_poly += 1

    # Geometry
    centroid = MeshGeometry.centroid(mesh)
    bbox = MeshGeometry.bounding_box(mesh)
    area = MeshGeometry.surface_area(mesh)
    volume = MeshGeometry.volume(mesh)

    is_3d = isinstance(mesh.vertices[0], Point3D) if mesh.vertices else False

    print("\n--- Mesh Information ---")
    print(f"File:           {args.input}")
    print(f"Dimensions:     {'3D' if is_3d else '2D'}")
    print(f"Nodes:          {n_nodes}")
    print(f"Edges:          {n_edges}")
    if n_faces > 0:
        print(f"Faces:          {n_faces}")
        print(f"  Triangles:    {n_tri}")
        print(f"  Quads:        {n_quad}")
        print(f"  Polygons:     {n_poly}")
    if n_cells > 0:
        print(f"Cells:          {n_cells}")

    print(f"\nCentroid:       {centroid}")

    if bbox:
        print(f"Bounding Box (AABB):")
        print(f"  Min: {bbox[0]}")
        print(f"  Max: {bbox[1]}")
        if is_3d:
            dims = (
                bbox[1][0] - bbox[0][0],
                bbox[1][1] - bbox[0][1],
                bbox[1][2] - bbox[0][2],
            )
        else:
            dims = (bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1])
        print(f"  Size: {dims}")

    if not is_3d and n_nodes > 0:
        obb = minimum_bounding_box(mesh.vertices)
        if obb:
            print(f"\nOriented Bounding Box (2D):")
            print(f"  Center: {obb['center']}")
            print(f"  Width:  {obb['width']:.6f}")
            print(f"  Height: {obb['height']:.6f}")
            print(f"  Area:   {obb['area']:.6f}")
            print(f"  Angle:  {obb['angle']:.6f} rad")

    print(f"\nSurface Area:   {area:.6f}")
    if is_3d:
        print(f"Volume:         {volume:.6f}")

    print(f"Watertight:     {'Yes' if topo.is_watertight() else 'No'}")
    if not n_cells:
        print(f"Orientable:     {'Yes' if topo.is_orientable() else 'No'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
