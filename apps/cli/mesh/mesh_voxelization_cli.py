from __future__ import annotations

import argparse
from compgeom import TriMesh, MeshVoxelizer, OBJFileHandler

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Voxelize a 3D triangular mesh.")
    parser.add_argument("--input", required=True, help="Path to input OBJ file.")
    parser.add_argument("--voxel_size", type=float, default=0.1, help="Voxel edge length")
    parser.add_argument("--method", choices=["auto", "native", "openvdb"], default="auto", help="Voxelization method")
    parser.add_argument("--fill", action="store_true", help="Fill the interior of the mesh")
    parser.add_argument("--output", help="Output file (only for openvdb method, .vdb)")
    
    args = parser.parse_args(argv)
    
    print(f"Reading mesh from {args.input}...")
    try:
        mesh = TriMesh.from_file(args.input)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1
        
    print(f"Mesh: {len(mesh.vertices)} vertices and {len(mesh.faces)} triangles.")
    
    if args.method == "auto":
        print(f"Voxelizing (auto) with voxel_size={args.voxel_size}...")
        result = MeshVoxelizer.voxelize(mesh, args.voxel_size, fill_interior=args.fill)
        if not hasattr(result, "save"):
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
        except Exception as e:
            print(f"Error: {e}")
            return 1
            
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
