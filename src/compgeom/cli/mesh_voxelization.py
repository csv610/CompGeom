import argparse
import sys
from compgeom.geometry import Point3D
from compgeom.mesh import TriangleMesh, MeshVoxelizer, OBJFileHandler

def create_cube():
    """Returns a TriangleMesh representing a unit cube."""
    vertices = [
        Point3D(0, 0, 0, 0), Point3D(1, 0, 0, 1), Point3D(1, 1, 0, 2), Point3D(0, 1, 0, 3),
        Point3D(0, 0, 1, 4), Point3D(1, 0, 1, 5), Point3D(1, 1, 1, 6), Point3D(0, 1, 1, 7)
    ]
    faces = [
        (0, 1, 2), (0, 2, 3), # Bottom
        (4, 5, 6), (4, 6, 7), # Top
        (0, 1, 5), (0, 5, 4), # Front
        (2, 3, 7), (2, 7, 6), # Back
        (0, 3, 7), (0, 7, 4), # Left
        (1, 2, 6), (1, 6, 5)  # Right
    ]
    return TriangleMesh(vertices, faces)

def main():
    parser = argparse.ArgumentParser(description="Voxelize a 3D triangular mesh.")
    parser.add_argument("--input", help="Path to input OBJ file (if not provided, a unit cube is used)")
    parser.add_argument("--voxel_size", type=float, default=0.1, help="Voxel edge length")
    parser.add_argument("--method", choices=["auto", "native", "openvdb"], default="auto", help="Voxelization method")
    parser.add_argument("--fill", action="store_true", help="Fill the interior of the mesh")
    parser.add_argument("--output", help="Output file (only for openvdb method, .vdb)")
    
    args = parser.parse_args()
    
    if args.input:
        print(f"Reading mesh from {args.input}...")
        mesh = TriangleMesh.from_file(args.input)
    else:
        mesh = create_cube()
        print("Using default unit cube mesh.")
        
    print(f"Mesh: {len(mesh.vertices)} vertices and {len(mesh.faces)} triangles.")
    
    if args.method == "auto":
        print(f"Voxelizing (auto) with voxel_size={args.voxel_size}...")
        result = MeshVoxelizer.voxelize(mesh, args.voxel_size, fill_interior=args.fill)
        if isinstance(result, set):
            print(f"Used native method. Generated {len(result)} voxels.")
        else:
            print("Used OpenVDB method. Successfully generated FloatGrid.")
            if args.output:
                MeshVoxelizer.save_vdb(result, args.output)
                print(f"Saved to {args.output}")
                
    elif args.method == "native":
        print(f"Voxelizing using native surface sampling (voxel_size={args.voxel_size}, fill={args.fill})...")
        voxels = MeshVoxelizer.voxelize_native(mesh, args.voxel_size, fill_interior=args.fill)
        print(f"Generated {len(voxels)} voxels.")
        
    elif args.method == "openvdb":
        print(f"Voxelizing using OpenVDB (voxel_size={args.voxel_size}, fill={args.fill})...")
        try:
            grid = MeshVoxelizer.voxelize_openvdb(mesh, args.voxel_size, fill_interior=args.fill)
            print("Successfully generated OpenVDB FloatGrid.")
            if args.output:
                MeshVoxelizer.save_vdb(grid, args.output)
                print(f"Saved to {args.output}")
        except ImportError as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
