"""Identify independent components in a mesh."""

from __future__ import annotations

from typing import List, Dict
from collections import deque

from compgeom.mesh.mesh_base import Mesh
from compgeom.mesh.mesh_topology import MeshTopology


class MeshComponents:
    """Provides algorithms for identifying connected components in a mesh."""

    @staticmethod
    def identify_vertex_components(mesh: Mesh) -> List[List[int]]:
        """
        Identifies connected components of vertices in the mesh.
        Two vertices are connected if there is an edge between them.
        
        Args:
            mesh: The Mesh object.
            
        Returns:
            A list of lists, where each sublist contains vertex indices in a component.
        """
        n_vertices = len(mesh.vertices)
        if n_vertices == 0:
            return []

        visited = [False] * n_vertices
        components = []
        
        for i in range(n_vertices):
            if not visited[i]:
                component = []
                queue = deque([i])
                visited[i] = True
                
                while queue:
                    u = queue.popleft()
                    component.append(u)
                    
                    # Adjacency for vertices
                    for v in MeshTopology(mesh).vertex_neighbors(u):
                        if not visited[v]:
                            visited[v] = True
                            queue.append(v)
                            
                components.append(component)
                
        return components

    @staticmethod
    def identify_face_components(mesh: Mesh) -> List[List[int]]:
        """
        Identifies connected components of faces (or cells) in the mesh.
        Two faces are connected if they share an edge.
        
        Args:
            mesh: The Mesh object.
            
        Returns:
            A list of lists, where each sublist contains face indices in a component.
        """
        # Determine number of elements (cells or faces)
        n_elements = 0
        if hasattr(mesh, 'cells') and mesh.cells is not None and len(mesh.cells) > 0:
            n_elements = len(mesh.cells)
        elif hasattr(mesh, 'faces') and mesh.faces is not None:
            n_elements = len(mesh.faces)
            
        if n_elements == 0:
            return []
            
        visited = [False] * n_elements
        components = []
        
        for i in range(n_elements):
            if not visited[i]:
                component = []
                queue = deque([i])
                visited[i] = True
                
                while queue:
                    u = queue.popleft()
                    component.append(u)
                    
                    # shared_edge_neighbors returns indices of faces/cells sharing an edge
                    for v in MeshTopology(mesh).shared_edge_neighbors(u):
                        if not visited[v]:
                            visited[v] = True
                            queue.append(v)
                            
                components.append(component)
                
        return components

    @staticmethod
    def get_component_statistics(mesh: Mesh) -> Dict[str, int]:
        """
        Calculates statistics about the connected components in the mesh.
        
        Returns:
            A dictionary containing counts and sizes of vertex and face components.
        """
        vertex_components = MeshComponents.identify_vertex_components(mesh)
        face_components = MeshComponents.identify_face_components(mesh)
        
        return {
            "num_vertex_components": len(vertex_components),
            "num_face_components": len(face_components),
            "max_vertex_component_size": max(len(c) for c in vertex_components) if vertex_components else 0,
            "min_vertex_component_size": min(len(c) for c in vertex_components) if vertex_components else 0,
            "max_face_component_size": max(len(c) for c in face_components) if face_components else 0,
            "min_face_component_size": min(len(c) for c in face_components) if face_components else 0
        }


__all__ = ["MeshComponents"]
