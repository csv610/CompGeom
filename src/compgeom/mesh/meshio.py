"""I/O utilities for 3D meshes (OBJ, OFF, STL, PLY formats)."""

from __future__ import annotations

import os
import struct
from typing import List, Tuple, Union, Optional

from ..kernel import Point2D, Point3D
from .mesh import Mesh, PolygonMesh, TriangleMesh


class OBJFileHandler:
    """Reader and writer for Wavefront OBJ files."""

    @staticmethod
    def read(filename: str) -> Mesh:
        """Reads an OBJ file and returns a Mesh object."""
        vertices: List[Union[Point2D, Point3D]] = []
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
                        vertices.append(Point2D(coords[0], coords[1], len(vertices)))

                elif prefix == "f":
                    face = []
                    for part in parts[1:]:
                        idx = int(part.split("/")[0])
                        if idx < 0:
                            face.append(len(vertices) + idx)
                        else:
                            face.append(idx - 1)
                    faces.append(face)

        return PolygonMesh(vertices, [tuple(f) for f in faces])

    @staticmethod
    def write(filename: str, mesh: Mesh, **kwargs):
        """Writes a Mesh object to an OBJ file.
        
        Args:
            filename: Path to the OBJ file.
            mesh: A Mesh object.
            **kwargs: Unused.
        """
        vertices = mesh.vertices
        faces = [c.v_indices for c in mesh.cells] if mesh.cells else [f.v_indices for f in mesh.faces]

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
    def read(filename: str) -> Mesh:
        """Reads an OFF file and returns a Mesh object."""
        vertices: List[Union[Point2D, Point3D]] = []
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
                    vertices.append(Point2D(coords[0], coords[1], i))
            
            for i in range(nf):
                parts = list(map(int, lines[start_idx + nv + i].split()))
                faces.append(parts[1:])
                
        return PolygonMesh(vertices, [tuple(f) for f in faces])

    @staticmethod
    def write(filename: str, mesh: Mesh, **kwargs):
        """Writes a Mesh object to an OFF file.
        
        Args:
            filename: Path to the OFF file.
            mesh: A Mesh object.
            **kwargs: Unused.
        """
        vertices = mesh.vertices
        faces = [c.v_indices for c in mesh.cells] if mesh.cells else [f.v_indices for f in mesh.faces]

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
    def read(filename: str) -> Mesh:
        """Reads an STL file (detects binary or ASCII) and returns a Mesh object."""
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
    def _read_binary(filename: str) -> Mesh:
        vertices: List[Union[Point2D, Point3D]] = []
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
        return TriangleMesh(vertices, [tuple(f) for f in faces])

    @staticmethod
    def _read_ascii(filename: str) -> Mesh:
        vertices: List[Union[Point2D, Point3D]] = []
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
        return TriangleMesh(vertices, [tuple(f) for f in faces])

    @staticmethod
    def write(filename: str, mesh: Mesh, binary: bool = True, **kwargs):
        """Writes a Mesh object to STL format (binary by default).
        
        Args:
            filename: Path to the STL file.
            mesh: A Mesh object.
            binary: Whether to write binary or ASCII STL.
            **kwargs: Unused.
        """
        vertices = mesh.vertices
        faces = [c.v_indices for c in mesh.cells] if mesh.cells else [f.v_indices for f in mesh.faces]

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
    def _write_binary(filename: str, vertices: List[Union[Point2D, Point3D]], faces: List[Tuple[int, int, int]]):
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
    def _write_ascii(filename: str, vertices: List[Union[Point2D, Point3D]], faces: List[Tuple[int, int, int]]):
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


class PLYFileHandler:
    """Reader and writer for Polygon File Format (PLY)."""

    @staticmethod
    def read(filename: str) -> Mesh:
        """Reads a PLY file (ASCII and Binary Little Endian) and returns a Mesh object."""
        vertices: List[Union[Point2D, Point3D]] = []
        faces: List[List[int]] = []

        with open(filename, "rb") as f:
            line = f.readline().strip()
            if line != b"ply":
                raise ValueError("Invalid PLY file: Missing 'ply' header")

            header = {}
            elements = []
            current_element = None

            while True:
                line_bytes = f.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("ascii").strip()
                if line == "end_header":
                    break
                
                parts = line.split()
                if not parts or parts[0] == "comment":
                    continue
                
                if parts[0] == "format":
                    header["format"] = parts[1]
                elif parts[0] == "element":
                    current_element = {"name": parts[1], "count": int(parts[2]), "properties": []}
                    elements.append(current_element)
                elif parts[0] == "property":
                    if current_element is not None:
                        current_element["properties"].append({"type": parts[1], "name": parts[-1], "raw": parts})
            
            if header["format"] == "ascii":
                for element in elements:
                    if element["name"] == "vertex":
                        for i in range(element["count"]):
                            line = f.readline().decode("ascii").strip()
                            coords = [float(x) for x in line.split()]
                            if len(coords) >= 3:
                                vertices.append(Point3D(coords[0], coords[1], coords[2], i))
                            else:
                                vertices.append(Point2D(coords[0], coords[1], i))
                    elif element["name"] == "face":
                        for i in range(element["count"]):
                            line = f.readline().decode("ascii").strip()
                            parts = [int(x) for x in line.split()]
                            faces.append(parts[1:])
            elif header["format"] == "binary_little_endian":
                type_map = {
                    "char": "b", "uchar": "B", "short": "h", "ushort": "H",
                    "int": "i", "uint": "I", "float": "f", "double": "d",
                    "int8": "b", "uint8": "B", "int16": "h", "uint16": "H",
                    "int32": "i", "uint32": "I", "float32": "f", "float64": "d"
                }
                
                for element in elements:
                    if element["name"] == "vertex":
                        fmt = "<"
                        for prop in element["properties"]:
                            fmt += type_map.get(prop["type"], "f")
                        
                        size = struct.calcsize(fmt)
                        for i in range(element["count"]):
                            data = f.read(size)
                            values = struct.unpack(fmt, data)
                            x, y, z = 0.0, 0.0, 0.0
                            found_z = False
                            for j, prop in enumerate(element["properties"]):
                                if prop["name"] == "x": x = values[j]
                                elif prop["name"] == "y": y = values[j]
                                elif prop["name"] == "z": 
                                    z = values[j]
                                    found_z = True
                            if found_z:
                                vertices.append(Point3D(x, y, z, i))
                            else:
                                vertices.append(Point2D(x, y, i))
                    elif element["name"] == "face":
                        for _ in range(element["count"]):
                            list_prop = element["properties"][0]
                            count_type = type_map[list_prop["raw"][2]]
                            index_type = type_map[list_prop["raw"][3]]
                            
                            count_size = struct.calcsize("<" + count_type)
                            count_data = f.read(count_size)
                            count = struct.unpack("<" + count_type, count_data)[0]
                            
                            indices_fmt = "<" + index_type * count
                            indices_size = struct.calcsize(indices_fmt)
                            indices_data = f.read(indices_size)
                            indices = struct.unpack(indices_fmt, indices_data)
                            faces.append(list(indices))
            else:
                raise ValueError(f"Unsupported PLY format: {header.get('format')}")

        return PolygonMesh(vertices, [tuple(f) for f in faces])

    @staticmethod
    def write(filename: str, mesh: Mesh, binary: bool = False, **kwargs):
        """Writes a Mesh object to a PLY file (ASCII by default).
        
        Args:
            filename: Path to the PLY file.
            mesh: A Mesh object.
            binary: Whether to write binary or ASCII PLY.
            **kwargs: Unused.
        """
        vertices = mesh.vertices
        faces = [c.v_indices for c in mesh.cells] if mesh.cells else [f.v_indices for f in mesh.faces]

        if binary:
            PLYFileHandler._write_binary(filename, vertices, faces)
        else:
            PLYFileHandler._write_ascii(filename, vertices, faces)

    @staticmethod
    def _write_ascii(filename: str, vertices: List[Union[Point2D, Point3D]], faces: List[Union[List[int], Tuple[int, ...]]]):
        with open(filename, "w") as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(vertices)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write(f"element face {len(faces)}\n")
            f.write("property list uchar int vertex_index\n")
            f.write("end_header\n")
            
            for v in vertices:
                z = getattr(v, 'z', 0.0)
                f.write(f"{v.x:.6f} {v.y:.6f} {z:.6f}\n")
            
            for face in faces:
                f.write(f"{len(face)} " + " ".join(map(str, face)) + "\n")

    @staticmethod
    def _write_binary(filename: str, vertices: List[Union[Point2D, Point3D]], faces: List[Union[List[int], Tuple[int, ...]]]):
        with open(filename, "wb") as f:
            f.write(b"ply\n")
            f.write(b"format binary_little_endian 1.0\n")
            f.write(f"element vertex {len(vertices)}\n".encode("ascii"))
            f.write(b"property float x\n")
            f.write(b"property float y\n")
            f.write(b"property float z\n")
            f.write(f"element face {len(faces)}\n".encode("ascii"))
            f.write(b"property list uchar int vertex_index\n")
            f.write(b"end_header\n")
            
            for v in vertices:
                z = getattr(v, 'z', 0.0)
                f.write(struct.pack("<fff", v.x, v.y, z))
            
            for face in faces:
                f.write(struct.pack("<B", len(face)))
                f.write(struct.pack(f"<{len(face)}i", *face))


class MeshImporter:
    """Unified interface for reading meshes in multiple formats."""

    _handlers = {
        ".obj": OBJFileHandler,
        ".off": OFFFileHandler,
        ".stl": STLFileHandler,
        ".ply": PLYFileHandler,
    }

    @classmethod
    def read(cls, filename: str) -> Mesh:
        """Detects format from extension and reads the file."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls._handlers:
            raise ValueError(f"Unsupported file format: {ext}")
        return cls._handlers[ext].read(filename)


class MeshExporter:
    """Unified interface for writing meshes in multiple formats."""

    _handlers = {
        ".obj": OBJFileHandler,
        ".off": OFFFileHandler,
        ".stl": STLFileHandler,
        ".ply": PLYFileHandler,
    }

    def __init__(self, mesh: Optional[Mesh] = None):
        """Initializes the exporter with an optional mesh object."""
        self._mesh: Optional[Mesh] = None
        if mesh is not None:
            self.mesh = mesh

    @property
    def mesh(self) -> Optional[Mesh]:
        """Gets the mesh object to be exported."""
        return self._mesh

    @mesh.setter
    def mesh(self, value: Mesh):
        """Sets the mesh object to be exported, validating it is a Mesh."""
        if not isinstance(value, Mesh):
            raise TypeError(f"Expected Mesh object, got {type(value).__name__}")
        self._mesh = value

    def export(self, filename: str, **kwargs):
        """Exports the assigned mesh to a file."""
        if self._mesh is None:
            raise ValueError("No mesh assigned to exporter.")
        self.write(filename, self._mesh, **kwargs)

    @classmethod
    def write(cls, filename: str, mesh: Mesh, **kwargs):
        """Detects format from extension and writes the file.
        
        Args:
            filename: Path to the output file.
            mesh: A Mesh object.
            **kwargs: Format-specific options (e.g., binary=True for STL/PLY).
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls._handlers:
            raise ValueError(f"Unsupported file format: {ext}")
        cls._handlers[ext].write(filename, mesh, **kwargs)


__all__ = ["from_file", "to_file", "MeshImporter", "MeshExporter", "OBJFileHandler", "OFFFileHandler", "STLFileHandler", "PLYFileHandler"]

def from_file(filename: str) -> Mesh:
    """Reads a mesh from a file using the MeshImporter."""
    return MeshImporter.read(filename)

def to_file(filename: str, mesh: Mesh, **kwargs) -> None:
    """Writes a mesh to a file using the MeshExporter."""
    MeshExporter.write(filename, mesh, **kwargs)
