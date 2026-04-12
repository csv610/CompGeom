from __future__ import annotations

import argparse
from compgeom import TriMesh, CuthillMcKee, OBJFileHandler

def calculate_dual_bandwidth(mesh: TriMesh) -> int:
    adj = {i: mesh.topology.shared_edge_neighbors(i) for i in range(len(mesh.faces))}
    bandwidth = 0
    for i, neighbors in adj.items():
        for j in neighbors:
            bandwidth = max(bandwidth, abs(i - j))
    return bandwidth

def calculate_nodal_bandwidth(mesh: TriMesh) -> int:
    adj = {i: mesh.topology.vertex_neighbors(i) for i in range(len(mesh.vertices))}
    bandwidth = 0
    for i, neighbors in adj.items():
        for j in neighbors:
            bandwidth = max(bandwidth, abs(i - j))
    return bandwidth

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reorder mesh elements or vertices using Cuthill-McKee.")
    parser.add_argument("--input", required=True, help="Path to input OBJ file.")
    parser.add_argument("--target", choices=["elements", "vertices"], default="elements", help="What to reorder")
    parser.add_argument("--no_reverse", action="store_true", help="Use standard Cuthill-McKee instead of Reverse (RCM)")
    parser.add_argument("--output", help="Path to output OBJ file with reordered mesh")
    
    args = parser.parse_args(argv)
    
    print(f"Reading mesh from {args.input}...")
    try:
        mesh = TriMesh.from_file(args.input)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1
        
    print(f"Mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} triangles.")
    
    if args.target == "elements":
        initial_bw = calculate_dual_bandwidth(mesh)
        print(f"Initial Dual Bandwidth: {initial_bw}")
        new_order = CuthillMcKee.reorder_elements(mesh, reverse=not args.no_reverse)
        reordered_faces = [mesh.faces[i] for i in new_order]
        new_mesh = TriMesh(mesh.vertices, reordered_faces)
        final_bw = calculate_dual_bandwidth(new_mesh)
    else:
        initial_bw = calculate_nodal_bandwidth(mesh)
        print(f"Initial Nodal Bandwidth: {initial_bw}")
        new_order = CuthillMcKee.reorder_vertices(mesh, reverse=not args.no_reverse)
        reordered_vertices = [mesh.vertices[i] for i in new_order]
        inv_map = {old: new for new, old in enumerate(new_order)}
        updated_faces = [tuple(inv_map[v] for v in f) for f in mesh.faces]
        new_mesh = TriMesh(reordered_vertices, updated_faces)
        final_bw = calculate_nodal_bandwidth(new_mesh)
        
    print(f"Final Bandwidth ({args.target}): {final_bw}")
    print(f"Bandwidth Reduction: {initial_bw - final_bw}")
    
    if args.output:
        OBJFileHandler.write(args.output, new_mesh)
        print(f"Saved reordered mesh to {args.output}") 

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
