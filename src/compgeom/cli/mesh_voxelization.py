import argparse
import sys
from compgeom.geometry import Point3D
from compgeom.voxelization import MeshVoxelizer
from compgeom.mesh_io import OBJFileHandler

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
    parser.add_argument("--input", help="Path to input OBJ file (if not provided, a unit cube is used)")
    parser.add_argument("--voxel_size", type=float, default=0.1, help="Voxel edge length")
    parser.add_argument("--method", choices=["native", "openvdb"], default="native", help="Voxelization method")
    parser.add_argument("--fill", action="store_true", help="Fill the interior of the mesh")
    parser.add_argument("--output", help="Output file (only for openvdb method, .vdb)")
    
    args = parser.parse_args()
    
    if args.input:
        print(f"Reading mesh from {args.input}...")
        vertices, faces = OBJFileHandler.read(args.input)
        # Ensure triangles
        faces = OBJFileHandler.triangulate_faces(faces)
    else:
        vertices, faces = create_cube()
        print("Using default unit cube mesh.")
        
    print(f"Mesh: {len(vertices)} vertices and {len(faces)} triangles.")
    
    if args.method == "native":
        print(f"Voxelizing using native surface sampling (voxel_size={args.voxel_size}, fill={args.fill})...")
        voxels = MeshVoxelizer.voxelize_native(vertices, faces, args.voxel_size, fill_interior=args.fill)
        print(f"Generated {len(voxels)} voxels.")
        # Print a few voxels
        sample = list(voxels)[:5]
        print(f"Sample voxels: {sample}")
        
    elif args.method == "openvdb":
        print(f"Voxelizing using OpenVDB (voxel_size={args.voxel_size}, fill={args.fill})...")
        try:
            grid = MeshVoxelizer.voxelize_openvdb(vertices, faces, args.voxel_size, fill_interior=args.fill)
            print("Successfully generated OpenVDB FloatGrid.")
            if args.output:
                MeshVoxelizer.save_vdb(grid, args.output)
                print(f"Saved to {args.output}")
        except ImportError as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
