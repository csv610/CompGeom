"""Surface mesh repair utilities."""

from __future__ import annotations
from collections import deque, defaultdict
from typing import List, Tuple, Set, Dict, Optional, Union

from ...mesh import TriangleMesh
from ...kernel import Point, Point3D


class SurfMeshRepair:
    """Repair tools for triangle meshes."""

    @staticmethod
    def remove_duplicate_points(mesh: TriangleMesh, epsilon: float = 1e-8) -> TriangleMesh:
        """Removes duplicate vertices and updates face indices."""
        old_vertices = mesh.vertices
        unique_vertices = []
        old_to_new = {}
        
        # Use rounding for stable hashing
        point_map = {}
        
        for i, v in enumerate(old_vertices):
            # Round coordinates to handle precision
            key = (round(v.x / epsilon), round(v.y / epsilon), round(getattr(v, 'z', 0.0) / epsilon))
            
            if key not in point_map:
                point_map[key] = len(unique_vertices)
                unique_vertices.append(v)
            
            old_to_new[i] = point_map[key]
            
        new_faces = []
        for face in mesh.faces:
            new_face = tuple(old_to_new[idx] for idx in face)
            # Avoid degenerate faces (two or more identical vertices)
            if len(set(new_face)) == 3:
                new_faces.append(new_face)
                
        return TriangleMesh(unique_vertices, new_faces)

    @staticmethod
    def remove_duplicate_faces(mesh: TriangleMesh) -> TriangleMesh:
        """Removes duplicate faces (identical vertex sets)."""
        seen_faces = set()
        unique_faces = []
        
        for face in mesh.faces:
            # Sort to identify same set of vertices regardless of order
            sorted_face = tuple(sorted(face))
            if sorted_face not in seen_faces:
                seen_faces.add(sorted_face)
                unique_faces.append(face)
                
        return TriangleMesh(mesh.vertices, unique_faces)

    @staticmethod
    def fix_normals(mesh: TriangleMesh) -> TriangleMesh:
        """Ensures all faces have consistent normal orientation using BFS."""
        faces = mesh.faces
        num_faces = len(faces)
        if num_faces == 0:
            return mesh
            
        # Build edge to face adjacency
        edge_to_faces = defaultdict(list)
        for i, face in enumerate(faces):
            for j in range(3):
                u, v = face[j], face[(j + 1) % 3]
                edge = tuple(sorted((u, v)))
                edge_to_faces[edge].append(i)
                
        new_faces = [None] * num_faces
        visited = [False] * num_faces
        
        # We might have multiple disconnected components
        for start_idx in range(num_faces):
            if visited[start_idx]:
                continue
                
            queue = deque([start_idx])
            new_faces[start_idx] = faces[start_idx]
            visited[start_idx] = True
            
            while queue:
                curr_idx = queue.popleft()
                curr_face = new_faces[curr_idx]
                
                # Check all edges of the current face
                for i in range(3):
                    u, v = curr_face[i], curr_face[(i + 1) % 3]
                    edge = tuple(sorted((u, v)))
                    
                    for neighbor_idx in edge_to_faces[edge]:
                        if not visited[neighbor_idx]:
                            neighbor_face = list(faces[neighbor_idx])
                            
                            # Find matching edge in neighbor
                            # In a manifold mesh, a shared edge (u, v) should have opposite direction
                            # if orientations are consistent.
                            found = False
                            for j in range(3):
                                nu, nv = neighbor_face[j], neighbor_face[(j + 1) % 3]
                                if {nu, nv} == {u, v}:
                                    # If edge is in same direction, flip neighbor
                                    if nu == u:
                                        neighbor_face[0], neighbor_face[1] = neighbor_face[1], neighbor_face[0]
                                    
                                    new_faces[neighbor_idx] = tuple(neighbor_face)
                                    visited[neighbor_idx] = True
                                    queue.append(neighbor_idx)
                                    found = True
                                    break
        
        # Filter out any None (shouldn't happen if BFS worked)
        final_faces = [f for f in new_faces if f is not None]
        return TriangleMesh(mesh.vertices, final_faces)

    @staticmethod
    def _get_triangle_coords(mesh: TriangleMesh, face_idx: int) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]:
        face = mesh.faces[face_idx]
        v0 = mesh.vertices[face[0]]
        v1 = mesh.vertices[face[1]]
        v2 = mesh.vertices[face[2]]
        return (
            (v0.x, v1.x, v2.x),
            (v0.y, v1.y, v2.y),
            (getattr(v0, 'z', 0.0), getattr(v1, 'z', 0.0), getattr(v2, 'z', 0.0))
        )

    @staticmethod
    def _tri_tri_intersect(tri1_pts: List[Union[Point, Point3D]], tri2_pts: List[Union[Point, Point3D]]) -> bool:
        """Simple triangle-triangle intersection test using SAT."""
        def get_coords(p):
            return [p.x, p.y, getattr(p, 'z', 0.0)]

        p1 = [get_coords(p) for p in tri1_pts]
        p2 = [get_coords(p) for p in tri2_pts]

        def dot(a, b):
            return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

        def cross(a, b):
            return [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]

        def sub(a, b):
            return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

        edges1 = [sub(p1[1], p1[0]), sub(p1[2], p1[1]), sub(p1[0], p1[2])]
        edges2 = [sub(p2[1], p2[0]), sub(p2[2], p2[1]), sub(p2[0], p2[2])]
        
        n1 = cross(edges1[0], edges1[1])
        n2 = cross(edges2[0], edges2[1])

        # Normal axes
        axes = [n1, n2]
        # Cross product of edges
        for e1 in edges1:
            for e2 in edges2:
                axes.append(cross(e1, e2))

        for axis in axes:
            if abs(axis[0]) < 1e-9 and abs(axis[1]) < 1e-9 and abs(axis[2]) < 1e-9:
                continue
            
            # Project tri1
            min1 = max1 = dot(axis, p1[0])
            for i in range(1, 3):
                val = dot(axis, p1[i])
                min1 = min(min1, val)
                max1 = max(max1, val)
                
            # Project tri2
            min2 = max2 = dot(axis, p2[0])
            for i in range(1, 3):
                val = dot(axis, p2[i])
                min2 = min(min2, val)
                max2 = max(max2, val)
                
            if max1 < min2 - 1e-9 or max2 < min1 - 1e-9:
                return False # Found separating axis
        
        return True

    @staticmethod
    def remove_self_intersections(mesh: TriangleMesh) -> TriangleMesh:
        """Removes one of each pair of self-intersecting faces."""
        faces = mesh.faces
        vertices = mesh.vertices
        num_faces = len(faces)
        
        to_remove = set()
        
        # Simple AABB for each triangle to speed up
        aabbs = []
        for face in faces:
            pts = [vertices[idx] for idx in face]
            min_x = min(p.x for p in pts)
            max_x = max(p.x for p in pts)
            min_y = min(p.y for p in pts)
            max_y = max(p.y for p in pts)
            min_z = min(getattr(p, 'z', 0.0) for p in pts)
            max_z = max(getattr(p, 'z', 0.0) for p in pts)
            aabbs.append((min_x, max_x, min_y, max_y, min_z, max_z))

        for i in range(num_faces):
            if i in to_remove:
                continue
            for j in range(i + 1, num_faces):
                if j in to_remove:
                    continue
                
                # Check if they share vertices - usually we don't count these as "self-intersection" 
                # unless they overlap, but SAT handles it. For efficiency, skip if they share 1 or 2 vertices
                if len(set(faces[i]) & set(faces[j])) > 0:
                    continue

                # AABB check
                a1 = aabbs[i]
                a2 = aabbs[j]
                if (a1[0] > a2[1] or a2[0] > a1[1] or
                    a1[2] > a2[3] or a2[2] > a1[3] or
                    a1[4] > a2[5] or a2[4] > a1[5]):
                    continue
                
                tri1_pts = [vertices[idx] for idx in faces[i]]
                tri2_pts = [vertices[idx] for idx in faces[j]]
                
                if SurfMeshRepair._tri_tri_intersect(tri1_pts, tri2_pts):
                    to_remove.add(j)

        new_faces = [faces[i] for i in range(num_faces) if i not in to_remove]
        return TriangleMesh(vertices, new_faces)

    @staticmethod
    def remove_degenerate_faces(mesh: TriangleMesh) -> TriangleMesh:
        """Removes faces with zero area or duplicate vertices."""
        new_faces = []
        for face in mesh.faces:
            if len(set(face)) == 3:
                # Check for near-zero area if vertices are Point3D
                v0, v1, v2 = [mesh.vertices[i] for i in face]
                # Vector cross product for area
                ux, uy, uz = v1.x - v0.x, v1.y - v0.y, getattr(v1, 'z', 0.0) - getattr(v0, 'z', 0.0)
                vx, vy, vz = v2.x - v0.x, v2.y - v0.y, getattr(v2, 'z', 0.0) - getattr(v0, 'z', 0.0)
                
                # Cross product components
                cx = uy * vz - uz * vy
                cy = uz * vx - ux * vz
                cz = ux * vy - uy * vx
                
                area_sq = cx*cx + cy*cy + cz*cz
                if area_sq > 1e-18: # epsilon for area
                    new_faces.append(face)
        return TriangleMesh(mesh.vertices, new_faces)

    @staticmethod
    def remove_non_manifold_faces(mesh: TriangleMesh) -> TriangleMesh:
        """Removes faces attached to edges shared by more than two faces."""
        faces = mesh.faces
        edge_to_faces = defaultdict(list)
        for i, face in enumerate(faces):
            for j in range(3):
                u, v = sorted((face[j], face[(j + 1) % 3]))
                edge_to_faces[(u, v)].append(i)
        
        to_remove = set()
        for edge, sharing_faces in edge_to_faces.items():
            if len(sharing_faces) > 2:
                # Non-manifold edge found. 
                # To satisfy "at most two", we remove all faces sharing this edge.
                for f_idx in sharing_faces:
                    to_remove.add(f_idx)
        
        new_faces = [faces[i] for i in range(len(faces)) if i not in to_remove]
        return TriangleMesh(mesh.vertices, new_faces)

    @staticmethod
    def remove_isolated_vertices(mesh: TriangleMesh) -> TriangleMesh:
        """Removes vertices that are not referenced by any face."""
        used_indices = set()
        for face in mesh.faces:
            used_indices.update(face)
        
        if len(used_indices) == len(mesh.vertices):
            return mesh
            
        old_to_new = {}
        new_vertices = []
        for i, v in enumerate(mesh.vertices):
            if i in used_indices:
                old_to_new[i] = len(new_vertices)
                new_vertices.append(v)
        
        new_faces = [tuple(old_to_new[idx] for idx in face) for face in mesh.faces]
        return TriangleMesh(new_vertices, new_faces)

    @staticmethod
    def remove_non_manifold_vertices(mesh: TriangleMesh) -> TriangleMesh:
        """Removes faces to ensure no vertex is non-manifold (pinch points)."""
        faces = mesh.faces
        if not faces:
            return mesh
            
        # Map each vertex to its incident faces
        v2f = defaultdict(list)
        for i, face in enumerate(faces):
            for v in face:
                v2f[v].append(i)
                
        to_remove = set()
        
        for v, incident_faces in v2f.items():
            if len(incident_faces) <= 1:
                continue
                
            # Build an adjacency graph of these faces based on sharing an edge containing 'v'
            adj = defaultdict(list)
            for i, f1_idx in enumerate(incident_faces):
                f1 = set(faces[f1_idx])
                for j in range(i + 1, len(incident_faces)):
                    f2_idx = incident_faces[j]
                    f2 = set(faces[f2_idx])
                    if len(f1 & f2) == 2:
                        adj[f1_idx].append(f2_idx)
                        adj[f2_idx].append(f1_idx)
            
            # Find connected components of faces around this vertex
            visited = set()
            components = []
            
            for f_idx in incident_faces:
                if f_idx in visited:
                    continue
                
                comp = []
                queue = deque([f_idx])
                visited.add(f_idx)
                
                while queue:
                    curr = queue.popleft()
                    comp.append(curr)
                    for nxt in adj[curr]:
                        if nxt not in visited:
                            visited.add(nxt)
                            queue.append(nxt)
                components.append(comp)
                
            # If more than 1 component, vertex is non-manifold (pinch point)
            if len(components) > 1:
                # Keep the largest continuous fan, prune the rest
                components.sort(key=len, reverse=True)
                for comp in components[1:]:
                    for f_idx in comp:
                        to_remove.add(f_idx)
                        
        if not to_remove:
            return mesh
            
        new_faces = [f for i, f in enumerate(faces) if i not in to_remove]
        return TriangleMesh(mesh.vertices, new_faces)

    @staticmethod
    def remove_small_components(mesh: TriangleMesh, min_fraction: float = 0.05) -> TriangleMesh:
        """Removes disconnected components that have fewer faces than a fraction of the largest component."""
        faces = mesh.faces
        if not faces:
            return mesh
            
        edge_to_faces = defaultdict(list)
        for i, face in enumerate(faces):
            for j in range(3):
                u, v = sorted((face[j], face[(j + 1) % 3]))
                edge_to_faces[(u, v)].append(i)
                
        visited = [False] * len(faces)
        components = []
        
        for start_idx in range(len(faces)):
            if visited[start_idx]:
                continue
            
            comp_faces = []
            queue = deque([start_idx])
            visited[start_idx] = True
            
            while queue:
                curr_idx = queue.popleft()
                comp_faces.append(curr_idx)
                curr_face = faces[curr_idx]
                
                for i in range(3):
                    u, v = sorted((curr_face[i], curr_face[(i + 1) % 3]))
                    for neighbor_idx in edge_to_faces[(u, v)]:
                        if not visited[neighbor_idx]:
                            visited[neighbor_idx] = True
                            queue.append(neighbor_idx)
            
            components.append(comp_faces)
            
        if not components:
            return mesh
            
        max_len = max(len(c) for c in components)
        threshold = max(1, int(max_len * min_fraction))
        
        keep_faces = []
        for comp in components:
            if len(comp) >= threshold:
                keep_faces.extend(comp)
                
        new_faces = [faces[i] for i in keep_faces]
        return TriangleMesh(mesh.vertices, new_faces)

    @staticmethod
    def orient_normals_outward(mesh: TriangleMesh) -> TriangleMesh:
        """Ensures normals for closed components point outward using signed volume."""
        faces = mesh.faces
        if not faces:
            return mesh
            
        # Group into components using edge adjacency
        edge_to_faces = defaultdict(list)
        for i, face in enumerate(faces):
            for j in range(3):
                u, v = sorted((face[j], face[(j + 1) % 3]))
                edge_to_faces[(u, v)].append(i)
                
        visited = [False] * len(faces)
        components = []
        
        for start_idx in range(len(faces)):
            if visited[start_idx]:
                continue
            
            comp_faces = []
            queue = deque([start_idx])
            visited[start_idx] = True
            
            while queue:
                curr_idx = queue.popleft()
                comp_faces.append(curr_idx)
                curr_face = faces[curr_idx]
                
                for i in range(3):
                    u, v = sorted((curr_face[i], curr_face[(i + 1) % 3]))
                    for neighbor_idx in edge_to_faces[(u, v)]:
                        if not visited[neighbor_idx]:
                            visited[neighbor_idx] = True
                            queue.append(neighbor_idx)
            
            components.append(comp_faces)
            
        new_faces = list(faces)
        vertices = mesh.vertices
        
        for comp in components:
            # Calculate signed volume for the component
            vol = 0.0
            for f_idx in comp:
                face = new_faces[f_idx]
                v0 = vertices[face[0]]
                v1 = vertices[face[1]]
                v2 = vertices[face[2]]
                
                # Treat as 3D for volume
                p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
                p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
                p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
                
                # Dot product of p0 with (p1 x p2)
                cross_x = p1[1]*p2[2] - p1[2]*p2[1]
                cross_y = p1[2]*p2[0] - p1[0]*p2[2]
                cross_z = p1[0]*p2[1] - p1[1]*p2[0]
                
                vol += p0[0]*cross_x + p0[1]*cross_y + p0[2]*cross_z
                
            # If volume is significantly negative, it means normals point inward
            if vol < -1e-9:
                for f_idx in comp:
                    f = new_faces[f_idx]
                    new_faces[f_idx] = (f[0], f[2], f[1])
                    
        return TriangleMesh(mesh.vertices, new_faces)

    @staticmethod
    def repair(mesh: TriangleMesh) -> TriangleMesh:
        """
        Applies all repair steps: 
        1. Remove duplicate/degenerate points and faces.
        2. Ensure simplicial (no self-intersections, no degenerates).
        3. Ensure manifold edges and vertices.
        4. Consistent and outward normals.
        5. Remove small dangling components.
        6. Clean up isolated vertices.
        """
        mesh = SurfMeshRepair.remove_duplicate_points(mesh)
        mesh = SurfMeshRepair.remove_degenerate_faces(mesh)
        mesh = SurfMeshRepair.remove_duplicate_faces(mesh)
        mesh = SurfMeshRepair.remove_non_manifold_faces(mesh)
        mesh = SurfMeshRepair.remove_non_manifold_vertices(mesh)
        mesh = SurfMeshRepair.remove_self_intersections(mesh)
        mesh = SurfMeshRepair.fix_normals(mesh)
        mesh = SurfMeshRepair.orient_normals_outward(mesh)
        mesh = SurfMeshRepair.remove_small_components(mesh)
        mesh = SurfMeshRepair.remove_isolated_vertices(mesh)
        return mesh
