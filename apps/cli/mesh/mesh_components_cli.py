from __future__ import annotations

import argparse
import sys
import os
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.mesh.algorithms.mesh_components import MeshComponents


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Identify and analyze connected components in a mesh."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-s", "--stats", action="store_true", help="Print summary statistics of components."
    )
    parser.add_argument(
        "-v", "--vertex-components", action="store_true", help="List vertex indices for each component."
    )
    parser.add_argument(
        "-f", "--face-components", action="store_true", help="List face indices for each component."
    )
    parser.add_argument(
        "-o", "--output-prefix", help="Prefix for saving each component as a separate mesh file."
    )

    args = parser.parse_args(argv)

    if not (args.stats or args.vertex_components or args.face_components or args.output_prefix):
        parser.print_help()
        return 0

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    if args.stats:
        stats = MeshComponents.get_component_statistics(mesh)
        print("Component Statistics:")
        print(f"  Vertex Components: {stats['num_vertex_components']}")
        print(f"    Max Size: {stats['max_vertex_component_size']}")
        print(f"    Min Size: {stats['min_vertex_component_size']}")
        print(f"  Face Components:   {stats['num_face_components']}")
        print(f"    Max Size: {stats['max_face_component_size']}")
        print(f"    Min Size: {stats['min_face_component_size']}")

    if args.vertex_components:
        v_comps = MeshComponents.identify_vertex_components(mesh)
        print(f"\nVertex Components ({len(v_comps)}):")
        for i, comp in enumerate(v_comps):
            print(f"  Component {i}: {len(comp)} vertices -> {comp[:10]}{'...' if len(comp) > 10 else ''}")

    if args.face_components:
        f_comps = MeshComponents.identify_face_components(mesh)
        print(f"\nFace Components ({len(f_comps)}):")
        for i, comp in enumerate(f_comps):
            print(f"  Component {i}: {len(comp)} faces -> {comp[:10]}{'...' if len(comp) > 10 else ''}")

    if args.output_prefix:
        f_comps = MeshComponents.identify_face_components(mesh)
        print(f"\nSaving {len(f_comps)} components...")
        
        ext = os.path.splitext(args.input)[1]
        if not ext: ext = ".off"
        
        from compgeom.mesh.surface.polygon.polygon import PolygonMesh
        
        for i, comp in enumerate(f_comps):
            # Extract vertices and faces for this component
            comp_face_indices = [mesh.faces[idx].v_indices for idx in comp]
            
            # Map old vertex indices to new local indices
            unique_v_indices = sorted(list(set(v for face in comp_face_indices for v in face)))
            old_to_new = {old: new for new, old in enumerate(unique_v_indices)}
            
            new_vertices = [mesh.vertices[idx] for idx in unique_v_indices]
            new_faces = [tuple(old_to_new[v] for v in face) for face in comp_face_indices]
            
            comp_mesh = PolygonMesh(new_vertices, new_faces)
            
            output_path = f"{args.output_prefix}_{i}{ext}"
            try:
                MeshExporter.write(output_path, comp_mesh)
                print(f"  Saved component {i} to {output_path}")
            except Exception as e:
                print(f"  Error saving component {i}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
