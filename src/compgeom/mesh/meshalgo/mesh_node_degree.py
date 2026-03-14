"""Calculates and displays mesh node degrees."""

from __future__ import annotations

from typing import Dict, List, Tuple

from compgeom.mesh import Mesh


class MeshNodeDegree:
    """Provides algorithms for calculating and displaying vertex degrees in a mesh."""

    @staticmethod
    def calculate_vertex_degrees(mesh: Mesh) -> List[int]:
        """
        Calculates the degree (number of incident edges) of each vertex in the mesh.
        
        Args:
            mesh: The Mesh object.
            
        Returns:
            A list of vertex degrees, where the index in the list corresponds to the vertex index.
        """
        n_vertices = len(mesh.vertices)
        degrees = []
        
        for i in range(n_vertices):
            # The degree of a vertex is the number of its neighbors
            neighbors = mesh.topology.vertex_neighbors(i)
            degrees.append(len(neighbors))
            
        return degrees

    @staticmethod
    def get_degree_statistics(mesh: Mesh) -> Dict[str, float]:
        """
        Calculates statistics about vertex degrees in the mesh.
        
        Returns:
            A dictionary containing 'min', 'max', 'average', and 'median' degrees.
        """
        degrees = MeshNodeDegree.calculate_vertex_degrees(mesh)
        if not degrees:
            return {"min": 0, "max": 0, "average": 0.0, "median": 0.0}
            
        degrees_sorted = sorted(degrees)
        n = len(degrees)
        
        min_deg = degrees_sorted[0]
        max_deg = degrees_sorted[-1]
        avg_deg = sum(degrees) / n
        
        if n % 2 == 1:
            median_deg = float(degrees_sorted[n // 2])
        else:
            median_deg = (degrees_sorted[n // 2 - 1] + degrees_sorted[n // 2]) / 2.0
            
        return {
            "min": min_deg,
            "max": max_deg,
            "average": avg_deg,
            "median": median_deg
        }

    @staticmethod
    def get_degree_distribution(mesh: Mesh) -> Dict[int, int]:
        """
        Calculates the frequency of each degree in the mesh.
        
        Returns:
            A dictionary mapping degree value to the number of vertices with that degree.
        """
        degrees = MeshNodeDegree.calculate_vertex_degrees(mesh)
        distribution = {}
        for d in degrees:
            distribution[d] = distribution.get(d, 0) + 1
        return distribution

    @staticmethod
    def generate_degree_table(mesh: Mesh) -> str:
        """
        Generates a formatted table string showing vertex indices and their degrees.
        Also includes a summary of degree statistics and counts for each degree.
        
        Returns:
            A formatted string containing the table, statistics, and counts.
        """
        degrees = MeshNodeDegree.calculate_vertex_degrees(mesh)
        stats = MeshNodeDegree.get_degree_statistics(mesh)
        distribution = MeshNodeDegree.get_degree_distribution(mesh)
        
        # Header
        table = [
            "Mesh Vertex Degree Table",
            "=" * 25,
            f"{'Vertex Index':<15} | {'Degree':<8}",
            "-" * 25
        ]
        
        # Table rows (limited to first 100 to avoid excessive output, can be adjusted)
        display_limit = 100
        for i, degree in enumerate(degrees[:display_limit]):
            table.append(f"{i:<15} | {degree:<8}")
            
        if len(degrees) > display_limit:
            table.append(f"... and {len(degrees) - display_limit} more vertices.")
            
        table.append("-" * 25)
        
        # Degree Counts (Distribution)
        table.extend([
            "",
            "Degree Counts (Distribution)",
            "=" * 25,
            f"{'Degree':<8} | {'Total Count':<12}",
            "-" * 25
        ])
        for degree in sorted(distribution.keys()):
            table.append(f"{degree:<8} | {distribution[degree]:<12}")
        table.append("-" * 25)
        
        # Statistics summary
        table.extend([
            "",
            "Degree Statistics",
            "=" * 25,
            f"Min Degree:     {stats['min']}",
            f"Max Degree:     {stats['max']}",
            f"Average Degree: {stats['average']:.2f}",
            f"Median Degree:  {stats['median']:.2f}",
            "=" * 25
        ])
        
        return "\n".join(table)


__all__ = ["MeshNodeDegree"]
