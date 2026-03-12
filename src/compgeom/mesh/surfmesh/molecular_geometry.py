"""Molecular geometry algorithms for drug design."""
from typing import List, Tuple, Dict
import math

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MolecularGeometry:
    """Provides algorithms for analyzing molecular surfaces and volumes."""

    @staticmethod
    def compute_sas(atomic_coordinates: List[Point3D], atomic_radii: List[float], probe_radius: float = 1.4) -> TriangleMesh:
        """
        Computes the Solvent Accessible Surface (SAS) of a molecule.
        Reconstructs the surface by rolling a spherical probe over the atoms.
        Approximated via Marching Cubes on a distance field.
        """
        from ..volmesh.marching_cubes import MarchingCubes
        
        # 1. Define the distance field: min(dist(p, atom_i) - (radius_i + probe))
        def sas_field(x, y, z):
            min_val = 1e9
            for p, r in zip(atomic_coordinates, atomic_radii):
                dist = math.sqrt((x-p.x)**2 + (y-p.y)**2 + (z-getattr(p, 'z', 0.0))**2)
                val = dist - (r + probe_radius)
                if val < min_val:
                    min_val = val
            return min_val

        # 2. Determine bounding box
        min_x = min(p.x - (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii))
        max_x = max(p.x + (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii))
        min_y = min(p.y - (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii))
        max_y = max(p.y + (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii))
        min_z = min(getattr(p, 'z', 0.0) - (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii))
        max_z = max(getattr(p, 'z', 0.0) + (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii))
        
        # 3. Extract isosurface at 0.0
        return MarchingCubes.reconstruct(sas_field, (min_x, min_y, min_z), (max_x, max_y, max_z), resolution=40)

    @staticmethod
    def molecular_volume(mesh: TriangleMesh) -> float:
        """Calculates the volume of the molecular surface (SAS or SES)."""
        from .mesh_analysis import MeshAnalysis
        return MeshAnalysis.total_volume(mesh)

    @staticmethod
    def detect_pockets(mesh: TriangleMesh, min_depth: float) -> List[List[int]]:
        """
        Identifies potential binding pockets/cavities on the protein surface.
        Uses Mean Curvature to find concave regions.
        """
        from .curvature import MeshCurvature
        mean_k = MeshCurvature.mean_curvature(mesh)
        
        # Pockets are regions of high negative mean curvature
        pocket_verts = [i for i, k in enumerate(mean_k) if k > min_depth] # Adjusting for magnitude sign
        
        # Cluster pocket vertices into individual cavities
        from collections import deque
        pockets = []
        visited = set()
        
        v2v = mesh.topology.vertex_neighbors_map()
        
        for v_idx in pocket_verts:
            if v_idx in visited: continue
            
            # BFS to find connected concave patch
            current_pocket = []
            queue = deque([v_idx])
            visited.add(v_idx)
            
            while queue:
                curr = queue.popleft()
                current_pocket.append(curr)
                for nb in v2v.get(curr, []):
                    if nb in pocket_verts and nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            pockets.append(current_pocket)
            
        return pockets
