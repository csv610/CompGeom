from __future__ import annotations
import math
import random
from typing import List, Tuple, Optional
from compgeom.kernel import Point3D, Ray
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.mesh.surface.mesh_queries import MeshQueries
from compgeom.mesh.surface.mesh_analysis import MeshAnalysis

class ShapeAnalysis:
    """
    Algorithms for shape analysis and feature extraction.
    """
    @staticmethod
    def compute_shape_diameter(mesh: SurfaceMesh, num_rays: int = 30, cone_angle: float = math.pi/3) -> List[float]:
        """
        Calculates the Shape Diameter Function (SDF) for each vertex of the mesh.
        SDF measures the local thickness of the object.
        """
        # 1. Compute vertex normals
        vertex_normals = MeshAnalysis.compute_vertex_normals(mesh)
        
        sdf_values = []
        for i, p in enumerate(mesh.vertices):
            # Casting a cone of rays into the interior
            # The "interior" is opposite to the normal vector
            normal = vertex_normals[i]
            inward_dir = Point3D(-normal[0], -normal[1], -normal[2])
            
            dists = []
            for _ in range(num_rays):
                # Generate a random ray within the cone
                ray_dir = ShapeAnalysis._get_random_cone_direction(inward_dir, cone_angle)
                
                # Intersect with the mesh
                # We need all intersections to find the opposite side
                p_tuple = (p.x, p.y, p.z)
                ray_dir_tuple = (ray_dir.x, ray_dir.y, ray_dir.z)
                intersections = MeshQueries.ray_intersect(mesh, p_tuple, ray_dir_tuple)
                
                # Filter out intersections with the starting face/point (t approx 0)
                # and sort by distance
                valid_hits = sorted([t for idx, t in intersections if t > 1e-6])
                
                if valid_hits:
                    # The first hit is the "opposite" side of the volume
                    dists.append(valid_hits[0])
            
            if dists:
                # Use median or average of distances within one standard deviation
                # to robustly estimate the diameter
                dists.sort()
                # Simple average for now
                sdf_values.append(sum(dists) / len(dists))
            else:
                sdf_values.append(0.0)
                
        return sdf_values

    @staticmethod
    def _get_random_cone_direction(axis: Point3D, max_angle: float) -> Point3D:
        """Generates a random unit vector within a cone around the given axis."""
        # 1. Create a local coordinate system around the axis
        axis = axis / axis.length()
        
        # Pick an arbitrary vector not parallel to axis
        temp = Point3D(1, 0, 0) if abs(axis.x) < 0.9 else Point3D(0, 1, 0)
        v = axis.cross(temp)
        v = v / v.length()
        u = axis.cross(v)
        
        # 2. Random spherical coordinates within the cone
        phi = random.uniform(0, 2 * math.pi)
        cos_theta = random.uniform(math.cos(max_angle), 1.0)
        sin_theta = math.sqrt(1.0 - cos_theta**2)
        
        # 3. Combine in local coordinates
        local_dir = u * (sin_theta * math.cos(phi)) + v * (sin_theta * math.sin(phi)) + axis * cos_theta
        return local_dir / local_dir.length()
