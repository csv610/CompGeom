from __future__ import annotations
import argparse
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from compgeom.mesh import meshio
from compgeom.mesh import MeshInformation

def process_file(file_path: str, parallel_ops: bool = True) -> dict | str:
    try:
        mesh = meshio.from_file(file_path)
        info = MeshInformation(mesh)
        info.compute(parallel=parallel_ops)
        return {"file": file_path, "info": info}
    except Exception as e:
        return f"Error processing {file_path}: {e}"

def print_info(res: dict):
    file_path = res["file"]
    info = res["info"]
    print(f"\n--- Mesh Information ---")
    print(f"File:           {file_path}")
    print(f"Dimensions:     {'3D' if info.is_3d else '2D'}")
    print(f"Nodes:          {info.n_nodes}")
    print(f"Edges:          {info.n_edges}")
    if info.n_faces > 0:
        print(f"Faces:          {info.n_faces}")
        print(f"  Triangles:    {info.n_tri}")
        print(f"  Quads:        {info.n_quad}")
        print(f"  Polygons:     {info.n_poly}")
    if info.n_cells > 0:
        print(f"Cells:          {info.n_cells}")

    print(f"\n--- Topology & Diagnostics ---")
    print(f"Components:     {info.n_components}")
    print(f"Euler Char:     {info.euler_characteristic}")
    print(f"Genus:          {info.genus:.1f}")
    print(f"Closed:         {'Yes' if info.is_watertight else 'No'}")
    print(f"Orientable:     {'Yes' if info.is_orientable else 'No'}")
    print(f"Oriented:       {'Yes' if info.is_oriented else 'No'}")
    print(f"Vertex Manifold:{'Yes' if not info.nm_verts else f'No ({len(info.nm_verts)} bad)'}")
    print(f"Edge Manifold:  {'Yes' if not info.nm_edges else f'No ({len(info.nm_edges)} bad)'}")
    print(f"Self-Intersect: {info.self_intersect}")
    print(f"Comb. Degenerate: {len(info.comb_deg) > 0}")
    print(f"Geom. Degenerate: {len(info.geom_deg) > 0}")
    print(f"Duplicate Faces: {len(info.dup_faces)}")
    print(f"Solid:          {'Yes' if info.is_solid else 'No'}")

    print(f"\n--- Geometry ---")
    if info.centroid:
        print(f"Centroid:       ({info.centroid.x:.4f}, {info.centroid.y:.4f}, {getattr(info.centroid, 'z', 0.0):.4f})")

    if info.bbox:
        print(f"Bounding Box (AABB):")
        print(f"  Min: {info.bbox[0]}")
        print(f"  Max: {info.bbox[1]}")
        print(f"  Size: {info.dims}")

    print(f"Surface Area:   {info.area:.6f}")
    if info.is_3d:
        print(f"Volume:         {info.volume:.6f}")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provide detailed information about 3D or 2D meshes."
    )
    parser.add_argument(
        "inputs", nargs="+", help="Path to the input mesh files (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "--no-parallel-ops", action="store_true", help="Disable parallel computation within each mesh."
    )
    parser.add_argument(
        "--no-parallel-files", action="store_true", help="Disable parallel processing of multiple files."
    )

    args = parser.parse_args(argv)

    if len(args.inputs) == 1 or args.no_parallel_files:
        for input_file in args.inputs:
            print(f"Processing {input_file}...")
            res = process_file(input_file, parallel_ops=not args.no_parallel_ops)
            if isinstance(res, str):
                print(res)
            else:
                print_info(res)
    else:
        print(f"Processing {len(args.inputs)} files in parallel...")
        # Use ProcessPoolExecutor for multi-file parallelism
        with ProcessPoolExecutor() as executor:
            future_to_file = {executor.submit(process_file, f, not args.no_parallel_ops): f for f in args.inputs}
            for future in as_completed(future_to_file):
                res = future.result()
                if isinstance(res, str):
                    print(res)
                else:
                    print_info(res)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
