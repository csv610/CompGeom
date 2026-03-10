"""I/O utilities for 3D meshes (OBJ, OFF, STL formats)."""

from __future__ import annotations

import os
import struct
from typing import List, Tuple, Union, Optional

from ..geo_math.geometry import Point, Point3D


class OBJFileHandler:
    """Reader and writer for Wavefront OBJ files."""

    @staticmethod
    def read(filename: str) -> Tuple[List[Union[Point, Point3D]], List[List[int]]]:
        """Reads an OBJ file and returns vertices and faces."""
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
                if not parts:
                    continue
                prefix = parts[0]

                if prefix == "v":
                    coords = [float(x) for x in parts[1:]]
                    if len(coords) >= 3:
                        vertices.append(Point3D(coords[0], coords[1], coords[2], len(vertices)))
                    elif len(coords) == 2:
                        vertices.append(Point(coords[0], coords[1], len(vertices)))

                elif prefix == "f":
                    face = []
                    for part in parts[1:]:
                        idx = int(part.split("/")[0])
                        if idx < 0:
                            face.append(len(vertices) + idx)
                        else:
                            face.append(idx - 1)
                    faces.append(face)

        return vertices, faces

    @staticmethod
    def triangulate_faces(faces: List[Union[List[int], Tuple[int, ...]]]) -> List[Tuple[int, int, int]]:
        """Converts arbitrary faces into triangles using fan triangulation."""
        tri_faces = []
        for face in faces:
            if len(face) == 3:
                tri_faces.append(tuple(face))
            elif len(face) > 3:
                for i in range(1, len(face) - 1):
                    tri_faces.append((face[0], face[i], face[i+1]))
        return tri_faces

    @staticmethod
    def write(filename: str, vertices: List[Union[Point, Point3D]], faces: List[Union[List[int], Tuple[int, ...]]]):
        """Writes vertices and faces to an OBJ file."""
        with open(filename, "w") as f:
            f.write("# Exported by CompGeom\n")
            for v in vertices:
                if isinstance(v, Point3D):
                    f.write(f"v {v.x:.6f} {v.y:.6f} {v.z:.6f}\n")
                else:
                    f.write(f"v {v.x:.6f} {v.y:.6f} 0.000000\n")

            for face in faces:
                f_str = " ".join(str(idx + 1) for idx in face)
                f.write(f"f {f_str}\n")


class OFFFileHandler:
    """Reader and writer for Object File Format (OFF)."""

    @staticmethod
    def read(filename: str) -> Tuple[List[Union[Point, Point3D]], List[List[int]]]:
        """Reads an OFF file."""
        vertices: List[Union[Point, Point3D]] = []
        faces: List[List[int]] = []

        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
            
            if not lines[0].startswith("OFF"):
                raise ValueError("Invalid OFF file: Missing OFF header")
            
            # The header might be on the same line as OFF or the next line
            if lines[0] == "OFF":
                header_line = lines[1]
                start_idx = 2
            else:
                header_line = lines[0][3:].strip()
                start_idx = 1
                
            nv, nf, _ = map(int, header_line.split())
            
            for i in range(nv):
                coords = list(map(float, lines[start_idx + i].split()))
                if len(coords) >= 3:
                    vertices.append(Point3D(coords[0], coords[1], coords[2], i))
                else:
                    vertices.append(Point(coords[0], coords[1], i))
            
            for i in range(nf):
                parts = list(map(int, lines[start_idx + nv + i].split()))
                faces.append(parts[1:])
                
        return vertices, faces

    @staticmethod
    def write(filename: str, vertices: List[Union[Point, Point3D]], faces: List[Union[List[int], Tuple[int, ...]]]):
        """Writes vertices and faces to an OFF file."""
        with open(filename, "w") as f:
            f.write("OFF\n")
            f.write(f"{len(vertices)} {len(faces)} 0\n")
            for v in vertices:
                z = getattr(v, 'z', 0.0)
                f.write(f"{v.x:.6f} {v.y:.6f} {z:.6f}\n")
            for face in faces:
                f.write(f"{len(face)} " + " ".join(map(str, face)) + "\n")


class STLFileHandler:
    """Reader and writer for STL (Binary and ASCII)."""

    @staticmethod
    def read(filename: str) -> Tuple[List[Union[Point, Point3D]], List[List[int]]]:
        """Reads an STL file (detects binary or ASCII)."""
        with open(filename, "rb") as f:
            header = f.read(80)
            if b"solid" in header[:10] and not STLFileHandler._is_binary(filename):
                return STLFileHandler._read_ascii(filename)
            else:
                return STLFileHandler._read_binary(filename)

    @staticmethod
    def _is_binary(filename: str) -> bool:
        file_size = os.path.getsize(filename)
        if file_size < 84: return False
        with open(filename, "rb") as f:
            f.seek(80)
            count = struct.unpack("<I", f.read(4))[0]
            return file_size == 84 + count * 50

    @staticmethod
    def _read_binary(filename: str) -> Tuple[List[Union[Point, Point3D]], List[List[int]]]:
        vertices: List[Union[Point, Point3D]] = []
        faces: List[List[int]] = []
        v_map = {}

        with open(filename, "rb") as f:
            f.read(80) # Skip header
            count = struct.unpack("<I", f.read(4))[0]
            for _ in range(count):
                f.read(12) # Skip normal
                face = []
                for _ in range(3):
                    xyz = struct.unpack("<fff", f.read(12))
                    key = tuple(round(c, 6) for c in xyz)
                    if key not in v_map:
                        v_idx = len(vertices)
                        v_map[key] = v_idx
                        vertices.append(Point3D(xyz[0], xyz[1], xyz[2], v_idx))
                    face.append(v_map[key])
                f.read(2) # Skip attribute byte count
                faces.append(face)
        return vertices, faces

    @staticmethod
    def _read_ascii(filename: str) -> Tuple[List[Union[Point, Point3D]], List[List[int]]]:
        vertices: List[Union[Point, Point3D]] = []
        faces: List[List[int]] = []
        v_map = {}
        
        with open(filename, "r") as f:
            face = []
            for line in f:
                line = line.strip().lower()
                if line.startswith("vertex"):
                    coords = list(map(float, line.split()[1:]))
                    key = tuple(round(c, 6) for c in coords)
                    if key not in v_map:
                        v_idx = len(vertices)
                        v_map[key] = v_idx
                        vertices.append(Point3D(coords[0], coords[1], coords[2], v_idx))
                    face.append(v_map[key])
                elif line.startswith("endfacet"):
                    faces.append(face)
                    face = []
        return vertices, faces

    @staticmethod
    def write(filename: str, vertices: List[Union[Point, Point3D]], faces: List[Union[List[int], Tuple[int, ...]]], binary: bool = True):
        """Writes a mesh to STL format (binary by default)."""
        # STL only supports triangles
        tri_faces = []
        for face in faces:
            if len(face) == 3:
                tri_faces.append(face)
            elif len(face) > 3:
                # Fan triangulation
                for i in range(1, len(face) - 1):
                    tri_faces.append((face[0], face[i], face[i+1]))
        
        if binary:
            STLFileHandler._write_binary(filename, vertices, tri_faces)
        else:
            STLFileHandler._write_ascii(filename, vertices, tri_faces)

    @staticmethod
    def _write_binary(filename: str, vertices: List[Union[Point, Point3D]], faces: List[Tuple[int, int, int]]):
        with open(filename, "wb") as f:
            f.write(b"CompGeom Binary STL".ljust(80, b"\0"))
            f.write(struct.pack("<I", len(faces)))
            for face in faces:
                f.write(struct.pack("<fff", 0, 0, 0)) # Normal
                for v_idx in face:
                    v = vertices[v_idx]
                    z = getattr(v, 'z', 0.0)
                    f.write(struct.pack("<fff", v.x, v.y, z))
                f.write(struct.pack("<H", 0))

    @staticmethod
    def _write_ascii(filename: str, vertices: List[Union[Point, Point3D]], faces: List[Tuple[int, int, int]]):
        with open(filename, "w") as f:
            f.write("solid compgeom\n")
            for face in faces:
                f.write("  facet normal 0 0 0\n")
                f.write("    outer loop\n")
                for v_idx in face:
                    v = vertices[v_idx]
                    z = getattr(v, 'z', 0.0)
                    f.write(f"      vertex {v.x:.6f} {v.y:.6f} {z:.6f}\n")
                f.write("    endloop\n")
                f.write("  endfacet\n")
            f.write("endsolid compgeom\n")


class MeshIO:
    """Unified interface for reading and writing meshes in multiple formats."""

    _handlers = {
        ".obj": OBJFileHandler,
        ".off": OFFFileHandler,
        ".stl": STLFileHandler,
    }

    @classmethod
    def read(cls, filename: str) -> Tuple[List[Union[Point, Point3D]], List[List[int]]]:
        """Detects format from extension and reads the file."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls._handlers:
            raise ValueError(f"Unsupported file format: {ext}")
        return cls._handlers[ext].read(filename)

    @classmethod
    def write(cls, filename: str, vertices: List[Union[Point, Point3D]], faces: List[Union[List[int], Tuple[int, ...]]], **kwargs):
        """Detects format from extension and writes the file."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls._handlers:
            raise ValueError(f"Unsupported file format: {ext}")
        cls._handlers[ext].write(filename, vertices, faces, **kwargs)


__all__ = ["MeshIO", "OBJFileHandler", "OFFFileHandler", "STLFileHandler"]
