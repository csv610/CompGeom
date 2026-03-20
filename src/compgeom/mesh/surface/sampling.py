"""Sampling utilities for meshes (surface and volume)."""
from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional
import math

from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.mesh.surface.mesh_queries import MeshQueries
from compgeom.kernel import Point3D

class MeshSampler:
    """Utilities for sampling points from mesh surface and volume."""

    @staticmethod
    def sample_surface(mesh: SurfaceMesh, num_samples: int) -> np.ndarray:
        """
        Uniformly samples points from the surface of the mesh.
        
        Args:
            mesh: The input mesh.
            num_samples: Total number of points to sample.
            
        Returns:
            An (N, 3) array of sampled points.
        """
        # 1. Compute areas of all triangles
        faces = mesh.faces
        verts = mesh.vertices
        areas = []
        for face in faces:
            v_idx = face.v_indices
            p0 = verts[v_idx[0]]
            p1 = verts[v_idx[1]]
            p2 = verts[v_idx[2]]
            
            # Cross product area
            ax, ay, az = p0.x, p0.y, getattr(p0, 'z', 0.0)
            bx, by, bz = p1.x, p1.y, getattr(p1, 'z', 0.0)
            cx, cy, cz = p2.x, p2.y, getattr(p2, 'z', 0.0)
            
            ux, uy, uz = bx - ax, by - ay, bz - az
            vx, vy, vz = cx - ax, cy - ay, cz - az
            
            area = 0.5 * math.sqrt((uy*vz - uz*vy)**2 + (uz*vx - ux*vz)**2 + (ux*vy - uy*vx)**2)
            areas.append(area)
            
        areas = np.array(areas)
        total_area = np.sum(areas)
        if total_area < 1e-12:
            return np.zeros((0, 3))
            
        # 2. Randomly select faces based on area weights
        probs = areas / total_area
        face_indices = np.random.choice(len(faces), size=num_samples, p=probs)
        
        # 3. Sample points within selected triangles
        samples = []
        for idx in face_indices:
            v_idx = faces[idx].v_indices
            p0 = verts[v_idx[0]]
            p1 = verts[v_idx[1]]
            p2 = verts[v_idx[2]]
            
            r1, r2 = np.random.rand(), np.random.rand()
            if r1 + r2 > 1:
                r1, r2 = 1 - r1, 1 - r2
                
            ax, ay, az = p0.x, p0.y, getattr(p0, 'z', 0.0)
            bx, by, bz = p1.x, p1.y, getattr(p1, 'z', 0.0)
            cx, cy, cz = p2.x, p2.y, getattr(p2, 'z', 0.0)
            
            sx = ax + r1 * (bx - ax) + r2 * (cx - ax)
            sy = ay + r1 * (by - ay) + r2 * (cy - ay)
            sz = az + r1 * (bz - az) + r2 * (cz - az)
            samples.append([sx, sy, sz])
            
        return np.array(samples)

    @staticmethod
    def sample_volume(mesh: SurfaceMesh, num_samples: int) -> np.ndarray:
        """
        Samples points from the interior volume of the mesh using rejection sampling.
        
        Args:
            mesh: The input mesh.
            num_samples: Target number of interior points.
            
        Returns:
            An (N, 3) array of sampled points.
        """
        # 1. Bounding box
        v_arr = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
        bmin = np.min(v_arr, axis=0)
        bmax = np.max(v_arr, axis=0)
        
        samples = []
        while len(samples) < num_samples:
            # Generate candidates in BB
            batch_size = max(10, num_samples - len(samples))
            candidates = np.random.uniform(bmin, bmax, (batch_size, 3))
            
            for p in candidates:
                # Use Generalized Winding Number for robust inside/outside check
                wn = MeshQueries.generalized_winding_number(mesh, tuple(p))
                if wn > 0.5:
                    samples.append(p)
                    if len(samples) >= num_samples:
                        break
                        
        return np.array(samples)
