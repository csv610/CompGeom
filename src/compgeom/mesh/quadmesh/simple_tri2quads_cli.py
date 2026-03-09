"""Conversion from TriangleMesh to QuadMesh via 1-to-3 splitting."""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Set, Tuple, Union

from ...geometry import Point, Point3D
from ..mesh import TriangleMesh, QuadMesh
from ..mesh_io import OBJFileHandler


class TriangleToQuadConverter:
    """Converts a TriangleMesh to a QuadMesh using midpoint-centroid splitting."""

    @staticmethod
    def convert(mesh: TriangleMesh) -> QuadMesh:
        """
        Transforms each triangle into 3 quadrilaterals.
        Each edge is split at its midpoint, and a vertex is added at the triangle centroid.
        """
        old_vertices = mesh.vertices
        old_faces = mesh.faces
        
        new_vertices = list(old_vertices)
        # edge_midpoints maps sorted tuple (v1, v2) to new vertex index
        edge_midpoints: Dict[Tuple[int, int], int] = {}
        
        def get_midpoint(i1: int, i2: int) -> int:
            edge = tuple(sorted((i1, i2)))
            if edge in edge_midpoints:
                return edge_midpoints[edge]
            
            v1, v2 = old_vertices[i1], old_vertices[i2]
            idx = len(new_vertices)
            
            if isinstance(v1, Point3D) and isinstance(v2, Point3D):
                mid = Point3D(
                    (v1.x + v2.x) / 2.0,
                    (v1.y + v2.y) / 2.0,
                    (v1.z + v2.z) / 2.0,
                    idx
                )
            else:
                mid = Point((v1.x + v2.x) / 2.0, (v1.y + v2.y) / 2.0, idx)
                
            new_vertices.append(mid)
            edge_midpoints[edge] = idx
            return idx

        quad_elements = []
        
        for face in old_faces:
            v0, v1, v2 = face
            
            # 1. Get/Create midpoints
            m01 = get_midpoint(v0, v1)
            m12 = get_midpoint(v1, v2)
            m20 = get_midpoint(v2, v0)
            
            # 2. Create centroid vertex
            c_idx = len(new_vertices)
            p0, p1, p2 = old_vertices[v0], old_vertices[v1], old_vertices[v2]
            
            if isinstance(p0, Point3D) and isinstance(p1, Point3D) and isinstance(p2, Point3D):
                centroid = Point3D(
                    (p0.x + p1.x + p2.x) / 3.0,
                    (p0.y + p1.y + p2.y) / 3.0,
                    (p0.z + p1.z + p2.z) / 3.0,
                    c_idx
                )
            else:
                centroid = Point(
                    (p0.x + p1.x + p2.x) / 3.0,
                    (p0.y + p1.y + p2.y) / 3.0,
                    c_idx
                )
            new_vertices.append(centroid)
            
            # 3. Create 3 quads
            # Quad 1: vertex 0, midpoint 01, centroid, midpoint 20
            quad_elements.append((v0, m01, c_idx, m20))
            # Quad 2: vertex 1, midpoint 12, centroid, midpoint 01
            quad_elements.append((v1, m12, c_idx, m01))
            # Quad 3: vertex 2, midpoint 20, centroid, midpoint 12
            quad_elements.append((v2, m20, c_idx, m12))
            
        return QuadMesh(new_vertices, quad_elements)


def main():
    parser = argparse.ArgumentParser(description="Convert TriangleMesh to QuadMesh (1-to-3 split).")
    parser.add_argument("input", help="Input OBJ file (TriangleMesh)")
    parser.add_argument("output", help="Output OBJ file (QuadMesh)")
    
    args = parser.parse_args()
    
    print(f"Reading triangle mesh from {args.input}...")
    try:
        vertices, faces = OBJFileHandler.read(args.input)
        # Ensure input is triangulated
        tri_faces = OBJFileHandler.triangulate_faces(faces)
        tri_mesh = TriangleMesh(vertices, tri_faces)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    print(f"Initial: {len(tri_mesh.vertices)} vertices, {len(tri_mesh.faces)} triangles.")
    
    quad_mesh = TriangleToQuadConverter.convert(tri_mesh)
    
    print(f"Converted: {len(quad_mesh.vertices)} vertices, {len(quad_mesh.faces)} quads.")
    
    print(f"Writing quad mesh to {args.output}...")
    OBJFileHandler.write(args.output, quad_mesh.vertices, quad_mesh.faces)
    print("Done.")


if __name__ == "__main__":
    main()
