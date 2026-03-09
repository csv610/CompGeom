import argparse
import sys
from compgeom.geometry import Point3D
from compgeom.voxelization import MeshVoxelizer

def create_cube():
    """Returns vertices and faces for a unit cube."""
    vertices = [
        Point3D(0, 0, 0, 0), Point3D(1, 0, 0, 1), Point3D(1, 1, 0, 2), Point3D(0, 1, 0, 3),
        Point3D(0, 0, 1, 4), Point3D(1, 0, 1, 5), Point3D(1, 1, 1, 6), Point3D(0, 1, 1, 7)
    ]
    # 12 triangles (2 per face)
    faces = [
        (0, 1, 2), (0, 2, 3), # Bottom
        (4, 5, 6), (4, 6, 7), # Top
        (0, 1, 5), (0, 5, 4), # Front
        (2, 3, 7), (2, 7, 6), # Back
        (0, 3, 7), (0, 7, 4), # Left
        (1, 2, 6), (1, 6, 5)  # Right
    ]
    return vertices, faces

def main():
    parser = argparse.ArgumentParser(description="Voxelize a 3D triangular mesh.")
    parser.add_argument("--voxel_size", type=float, default=0.1, help="Voxel edge length")
    parser.add_argument("--method", choices=["native", "openvdb"], default="native", help="Voxelization method")
    parser.add_argument("--output", help="Output file (only for openvdb method, .vdb)")
    
    args = parser.parse_args()
    
    vertices, faces = create_cube()
    print(f"Mesh: Cube with {len(vertices)} vertices and {len(faces)} triangles.")
    
    if args.method == "native":
        print(f"Voxelizing using native surface sampling (voxel_size={args.voxel_size})...")
        voxels = MeshVoxelizer.voxelize_native(vertices, faces, args.voxel_size)
        print(f"Generated {len(voxels)} surface voxels.")
        # Print a few voxels
        sample = list(voxels)[:5]
        print(f"Sample voxels: {sample}")
        
    elif args.method == "openvdb":
        print(f"Voxelizing using OpenVDB (voxel_size={args.voxel_size})...")
        try:
            grid = MeshVoxelizer.voxelize_openvdb(vertices, faces, args.voxel_size)
            print("Successfully generated OpenVDB FloatGrid.")
            if args.output:
                MeshVoxelizer.save_vdb(grid, args.output)
                print(f"Saved to {args.output}")
        except ImportError as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
