"""I/O utilities for 3D meshes (OBJ format)."""

from __future__ import annotations

import os
from typing import List, Tuple, Union

from ..geo_math.geometry import Point, Point3D


class OBJFileHandler:
    """Reader and writer for Wavefront OBJ files."""

    @staticmethod
    def read(filename: str) -> Tuple[List[Union[Point, Point3D]], List[List[int]]]:
        """
        Reads an OBJ file and returns vertices and faces.
        Faces are returned as lists of 0-based vertex indices.
        """
        vertices: List[Union[Point, Point3D]] = []
        faces: List[List[int]] = []

        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")

        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                prefix = parts[0]

                if prefix == "v":
                    # Vertex
                    coords = [float(x) for x in parts[1:4]]
                    if len(coords) == 3:
                        vertices.append(Point3D(coords[0], coords[1], coords[2], len(vertices)))
                    else:
                        vertices.append(Point(coords[0], coords[1], len(vertices)))

                elif prefix == "f":
                    # Face (handle v, v/vt, v/vt/vn)
                    face = []
                    for part in parts[1:]:
                        # OBJ uses 1-based indexing
                        idx = int(part.split("/")[0])
                        # Handle negative indices (relative to end)
                        if idx < 0:
                            face.append(len(vertices) + idx)
                        else:
                            face.append(idx - 1)
                    faces.append(face)

        return vertices, faces

    @staticmethod
    def write(
        filename: str, 
        vertices: List[Union[Point, Point3D]], 
        faces: List[Union[List[int], Tuple[int, ...]]]
    ):
        """Writes vertices and faces to an OBJ file."""
        with open(filename, "w") as f:
            f.write(f"# Exported by CompGeom\n")
            f.write(f"# Vertices: {len(vertices)}\n")
            f.write(f"# Faces: {len(faces)}\n")

            for v in vertices:
                if isinstance(v, Point3D):
                    f.write(f"v {v.x:.6f} {v.y:.6f} {v.z:.6f}\n")
                else:
                    f.write(f"v {v.x:.6f} {v.y:.6f} 0.000000\n")

            for face in faces:
                # OBJ uses 1-based indexing
                f_str = " ".join(str(idx + 1) for idx in face)
                f.write(f"f {f_str}\n")

    @staticmethod
    def triangulate_faces(faces: List[List[int]]) -> List[Tuple[int, int, int]]:
        """Converts arbitrary polygon faces into triangles using fan triangulation."""
        triangles = []
        for face in faces:
            if len(face) < 3:
                continue
            # Fan triangulation (works for convex polygons)
            for i in range(1, len(face) - 1):
                triangles.append((face[0], face[i], face[i + 1]))
        return triangles


__all__ = ["OBJFileHandler"]
