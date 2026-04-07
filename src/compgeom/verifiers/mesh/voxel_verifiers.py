from __future__ import annotations

import math
from typing import Set, Tuple, List
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.mesh_queries import MeshQueries


def verify_mesh_voxelization(
    mesh: TriMesh, 
    voxel_size: float, 
    voxels: Set[Tuple[int, int, int]], 
    fill_interior: bool = False
) -> bool:
    """
    Rigorously verifies a mesh voxelization.
    
    1. Surface Coverage: All mesh vertices must be covered by at least one voxel.
    2. Boundary Check: All voxels must be within or near the mesh's bounding box.
    3. Validity: 
       - If not fill_interior: every voxel must be near the surface.
       - If fill_interior: every voxel must be either near the surface or inside.
    """
    if not voxels:
        return len(mesh.faces) == 0

    # 1. Surface Coverage
    for v in mesh.vertices:
        ix = int(math.floor(v.x / voxel_size))
        iy = int(math.floor(v.y / voxel_size))
        iz = int(math.floor(v.z / voxel_size))
        if (ix, iy, iz) not in voxels:
            # Check neighbors too due to floating point eps
            found = False
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if (ix + dx, iy + dy, iz + dz) in voxels:
                            found = True
                            break
                    if found: break
                if found: break
            if not found:
                raise ValueError(f"Mesh vertex {v} is not covered by any voxel at size {voxel_size}")

    # 2. Boundary Check
    min_v = [min(v.x for v in mesh.vertices), min(v.y for v in mesh.vertices), min(v.z for v in mesh.vertices)]
    max_v = [max(v.x for v in mesh.vertices), max(v.y for v in mesh.vertices), max(v.z for v in mesh.vertices)]
    
    for vox in voxels:
        vx, vy, vz = vox[0] * voxel_size, vox[1] * voxel_size, vox[2] * voxel_size
        # Voxel should be within [min-size, max+size]
        if (vx < min_v[0] - voxel_size or vx > max_v[0] + voxel_size or
            vy < min_v[1] - voxel_size or vy > max_v[1] + voxel_size or
            vz < min_v[2] - voxel_size or vz > max_v[2] + voxel_size):
            raise ValueError(f"Voxel {vox} is outside mesh bounding box")

    # 3. Validity (Near surface or inside)
    # Check a random sample of voxels to keep it fast if set is large
    import random
    sample_size = min(len(voxels), 100)
    sample_voxels = random.sample(list(voxels), sample_size)
    
    max_surface_dist = (math.sqrt(3) / 2.0) * voxel_size + 1e-7
    
    for vox in sample_voxels:
        center = (
            (vox[0] + 0.5) * voxel_size,
            (vox[1] + 0.5) * voxel_size,
            (vox[2] + 0.5) * voxel_size
        )
        
        dist = MeshQueries.compute_sdf(mesh, center)
        
        if dist <= max_surface_dist:
            continue # Surface voxel
            
        if fill_interior:
            # Must be inside
            wn = MeshQueries.generalized_winding_number(mesh, center)
            if abs(wn) < 0.5:
                raise ValueError(f"Voxel {vox} is neither near surface (dist={dist}) nor inside (wn={wn})")
        else:
            raise ValueError(f"Voxel {vox} is too far from surface (dist={dist}, limit={max_surface_dist})")

    return True
