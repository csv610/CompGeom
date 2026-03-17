import argparse
import sys
from compgeom import Point2D
from compgeom import TriangleMesh, CuthillMcKee, OBJFileHandler

def calculate_dual_bandwidth(mesh: TriangleMesh):
    adj = {i: mesh.topology.shared_edge_neighbors(i) for i in range(len(mesh.faces))}
    bandwidth = 0
    for i, neighbors in adj.items():
        for j in neighbors:
            bandwidth = max(bandwidth, abs(i - j))
    return bandwidth

def calculate_nodal_bandwidth(mesh: TriangleMesh):
    adj = {i: mesh.topology.vertex_neighbors(i) for i in range(len(mesh.vertices))}
    bandwidth = 0
    for i, neighbors in adj.items():
        for j in neighbors:
            bandwidth = max(bandwidth, abs(i - j))
    return bandwidth

def main():
    parser = argparse.ArgumentParser(description="Reorder mesh elements or vertices using Cuthill-McKee.")
    parser.add_argument("--input", help="Path to input OBJ file (if not provided, a simple 2D grid is used)")
    parser.add_argument("--target", choices=["elements", "vertices"], default="elements", help="What to reorder")
    parser.add_argument("--no_reverse", action="store_true", help="Use standard Cuthill-McKee instead of Reverse (RCM)")
    parser.add_argument("--output", help="Path to output OBJ file with reordered mesh")
    
    args = parser.parse_args()
    
    if args.input:
        print(f"Reading mesh from {args.input}...")
        mesh = TriangleMesh.from_file(args.input)
    else:
        # Create a shuffled grid
        import random
        vertices = [Point2D(x,y) for y in range(4) for x in range(4)]
        faces = []
        for j in range(3):
            for i in range(3):
                v0, v1, v2, v3 = j*4+i, j*4+i+1, (j+1)*4+i, (j+1)*4+i+1
                faces.extend([(v0, v1, v3), (v0, v3, v2)])
        random.seed(42)
        random.shuffle(faces)
        v_map = list(range(len(vertices)))
        random.shuffle(v_map)
        shuffled_vertices = [vertices[i] for i in v_map]
        inv_map = {old: new for new, old in enumerate(v_map)}
        shuffled_faces = [tuple(inv_map[v] for v in f) for f in faces]
        mesh = TriangleMesh(shuffled_vertices, shuffled_faces)
        print("Using default shuffled 3x3 grid.")
        
    print(f"Mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} triangles.")
    
    if args.target == "elements":
        initial_bw = calculate_dual_bandwidth(mesh)
        print(f"Initial Dual Bandwidth: {initial_bw}")
        new_order = CuthillMcKee.reorder_elements(mesh, reverse=not args.no_reverse)
        reordered_faces = [mesh.faces[i] for i in new_order]
        new_mesh = TriangleMesh(mesh.vertices, reordered_faces)
        final_bw = calculate_dual_bandwidth(new_mesh)
    else:
        initial_bw = calculate_nodal_bandwidth(mesh)
        print(f"Initial Nodal Bandwidth: {initial_bw}")
        new_order = CuthillMcKee.reorder_vertices(mesh, reverse=not args.no_reverse)
        # Reorder vertices
        reordered_vertices = [mesh.vertices[i] for i in new_order]
        inv_map = {old: new for new, old in enumerate(new_order)}
        updated_faces = [tuple(inv_map[v] for v in f) for f in mesh.faces]
        new_mesh = TriangleMesh(reordered_vertices, updated_faces)
        final_bw = calculate_nodal_bandwidth(new_mesh)
        
    print(f"Final Bandwidth ({args.target}): {final_bw}")
    print(f"Bandwidth Reduction: {initial_bw - final_bw}")
    
    if args.output:
        OBJFileHandler.write(args.output, new_mesh)
        print(f"Saved reordered mesh to {args.output}") 

    return 0

if __name__ == "__main__":
    main()
