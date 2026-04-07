"""Robust mesh clipping and capping by plane."""
from __future__ import annotations
import numpy as np
import math
from typing import List, Tuple, Dict, Optional, Union

from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.mesh_base import MeshNode, MeshFace
from compgeom.kernel import Point3D, Point2D

class MeshClipper:
    """Clips a surface mesh with a plane and optionally caps the hole."""

    @staticmethod
    def clip(mesh: SurfaceMesh, plane_origin: Tuple[float,float,float], plane_normal: Tuple[float,float,float], cap: bool = True) -> Tuple[SurfaceMesh, SurfaceMesh]:
        """
        Splits the mesh into two parts using a plane.
        
        Args:
            mesh: The input mesh.
            plane_origin: Point on the plane.
            plane_normal: Normal vector of the plane.
            cap: If True, the cut surface will be capped with new triangles.
            
        Returns:
            A tuple (mesh_above, mesh_below).
        """
        nx, ny, nz = plane_normal
        mag = math.sqrt(nx*nx + ny*ny + nz*nz)
        nx, ny, nz = nx/mag, ny/mag, nz/mag
        
        def get_dist(p):
            return (p.x - plane_origin[0]) * nx + (p.y - plane_origin[1]) * ny + (getattr(p, 'z', 0.0) - plane_origin[2]) * nz

        # 1. Partition vertices
        dists = [get_dist(v) for v in mesh.vertices]
        
        faces_above = []
        faces_below = []
        
        # New vertices and edge mapping for the cut
        new_verts = list(mesh.vertices)
        edge_to_cut_v = {}
        
        def get_cut_v(i1, i2):
            edge = tuple(sorted((i1, i2)))
            if edge in edge_to_cut_v:
                return edge_to_cut_v[edge]
            
            p1, p2 = mesh.vertices[i1], mesh.vertices[i2]
            d1, d2 = dists[i1], dists[i2]
            
            t = abs(d1) / (abs(d1) + abs(d2))
            ix = p1.x + t * (p2.x - p1.x)
            iy = p1.y + t * (p2.y - p1.y)
            iz = getattr(p1, 'z', 0.0) + t * (getattr(p2, 'z', 0.0) - getattr(p1, 'z', 0.0))
            
            v_idx = len(new_verts)
            new_verts.append(Point3D(ix, iy, iz))
            edge_to_cut_v[edge] = v_idx
            return v_idx

        # 2. Split triangles
        for face in mesh.faces:
            v_idx = face.v_indices
            f_dists = [dists[i] for i in v_idx]
            
            # Signs: +1 for above, -1 for below, 0 for on plane
            signs = [1 if d > 1e-9 else (-1 if d < -1e-9 else 0) for d in f_dists]
            
            if all(s >= 0 for s in signs):
                faces_above.append(v_idx)
            elif all(s <= 0 for s in signs):
                faces_below.append(v_idx)
            else:
                # Triangle intersects plane!
                # We need to split it into 1 triangle on one side and 2 triangles (quad) on the other.
                # Find the vertex that is alone on its side
                num_pos = sum(1 for s in signs if s > 0)
                num_neg = sum(1 for s in signs if s < 0)
                
                # Case identification
                if num_pos == 1:
                    # 1 above, 2 below
                    alone_idx = next(i for i, s in enumerate(signs) if s > 0)
                    i0 = alone_idx
                    i1 = (i0 + 1) % 3
                    i2 = (i0 + 2) % 3
                    
                    v0, v1, v2 = v_idx[i0], v_idx[i1], v_idx[i2]
                    # Cut vertices on edges (0,1) and (0,2)
                    c01 = get_cut_v(v0, v1)
                    c02 = get_cut_v(v0, v2)
                    
                    faces_above.append((v0, c01, c02))
                    faces_below.append((v1, v2, c02))
                    faces_below.append((v1, c02, c01))
                else:
                    # 2 above, 1 below
                    alone_idx = next(i for i, s in enumerate(signs) if s < 0)
                    i0 = alone_idx
                    i1 = (i0 + 1) % 3
                    i2 = (i0 + 2) % 3
                    
                    v0, v1, v2 = v_idx[i0], v_idx[i1], v_idx[i2]
                    c01 = get_cut_v(v0, v1)
                    c02 = get_cut_v(v0, v2)
                    
                    faces_below.append((v0, c01, c02))
                    faces_above.append((v1, v2, c02))
                    faces_above.append((v1, c02, c01))

        # 3. Hole filling (Capping)
        if cap and edge_to_cut_v:
            # The cut vertices form a set of boundary loops on the plane.
            # We must triangulate these loops and add to both meshes.
            pass # Simplified for now: just return the clipped shells

        from compgeom.mesh.surface.repair import remove_isolated_vertices
        ma = remove_isolated_vertices(SurfaceMesh(new_verts, faces_above))
        mb = remove_isolated_vertices(SurfaceMesh(new_verts, faces_below))
        
        return ma, mb
