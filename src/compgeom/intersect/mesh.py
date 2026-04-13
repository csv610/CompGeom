from __future__ import annotations
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from compgeom.mesh.surface.surface_mesh import SurfaceMesh

def ray_mesh_intersect(mesh: SurfaceMesh, origin: Tuple[float, float, float], 
                      direction: Tuple[float, float, float], use_spatial: bool = True) -> List[Tuple[int, float]]:
    """Returns all intersections between a ray and a surface mesh."""
    if use_spatial:
        from compgeom.mesh.surface.spatial_acceleration import AABBTree
        tree = AABBTree(mesh)
        return tree.ray_intersect(origin, direction)
    
    from compgeom.mesh.surface.mesh_queries import MeshQueries
    intersections = []
    for i in range(len(mesh.faces)):
        t = MeshQueries._single_ray_face_intersect(mesh, i, origin, direction)
        if t is not None: intersections.append((i, t))
    return sorted(intersections, key=lambda x: x[1])

def mesh_mesh_intersect(mesh_a: SurfaceMesh, mesh_b: SurfaceMesh) -> List[Tuple[int, int]]:
    """Detects intersections between two meshes."""
    from compgeom.mesh.surface.spatial_acceleration import AABBTree
    from compgeom.intersect.primitive import tri_tri_intersect
    
    tree_a, tree_b = AABBTree(mesh_a), AABBTree(mesh_b)
    results = []

    def intersect_nodes(node_a, node_b):
        if not node_a or not node_b: return
        # AABB overlap check
        if (node_a.bmin[0] > node_b.bmax[0] or node_b.bmin[0] > node_a.bmax[0] or
            node_a.bmin[1] > node_b.bmax[1] or node_b.bmin[1] > node_a.bmax[1] or
            node_a.bmin[2] > node_b.bmax[2] or node_b.bmin[2] > node_a.bmax[2]):
            return
        if node_a.is_leaf() and node_b.is_leaf():
            for fa_idx in node_a.faces:
                for fb_idx in node_b.faces:
                    pts_a = [mesh_a.vertices[i] for i in mesh_a.faces[fa_idx]]
                    pts_b = [mesh_b.vertices[i] for i in mesh_b.faces[fb_idx]]
                    if tri_tri_intersect(pts_a, pts_b):
                        results.append((fa_idx, fb_idx))
        elif node_a.is_leaf():
            intersect_nodes(node_a, node_b.left); intersect_nodes(node_a, node_b.right)
        elif node_b.is_leaf():
            intersect_nodes(node_a.left, node_b); intersect_nodes(node_a.right, node_b)
        else:
            intersect_nodes(node_a.left, node_b.left); intersect_nodes(node_a.left, node_b.right)
            intersect_nodes(node_a.right, node_b.left); intersect_nodes(node_a.right, node_b.right)

    intersect_nodes(tree_a.root, tree_b.root)
    return results
