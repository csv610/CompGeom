"""Mesh Importer and Exporter for STL, OFF, and OBJ formats."""

from __future__ import annotations
import os
from typing import TYPE_CHECKING, List, Tuple

from ...kernel import Point

if TYPE_CHECKING:
    from ..mesh import TriangleMesh


class MeshImporter:
    """Imports meshes from various file formats."""

    @staticmethod
    def import_mesh(file_path: str) -> TriangleMesh:
        """
        Imports a mesh from a file.
        Detects format based on file extension.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".off":
            return MeshImporter.import_off(file_path)
        elif ext == ".obj":
            return MeshImporter.import_obj(file_path)
        elif ext == ".stl":
            return MeshImporter.import_stl(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def import_off(file_path: str) -> TriangleMesh:
        """Imports an OFF (Object File Format) file."""
        from ..mesh import TriangleMesh
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Clean lines: remove comments and empty lines
        lines = [line.split('#')[0].strip() for line in lines]
        lines = [line for line in lines if line]

        if not lines or lines[0] != 'OFF':
            # Some OFF files have OFF and numbers on the same line
            if lines[0].startswith('OFF'):
                lines[0] = lines[0][3:].strip()
            else:
                raise ValueError("Not a valid OFF file")
        else:
            lines.pop(0)

        # Parse counts
        counts = list(map(int, lines[0].split()))
        n_verts, n_faces = counts[0], counts[1]
        lines.pop(0)

        # Parse vertices
        vertices = []
        for i in range(n_verts):
            coords = list(map(float, lines[i].split()))
            # Handle 2D or 3D (ignore Z for now if we only support 2D points in kernel)
            vertices.append(Point(coords[0], coords[1], id=i))
        
        # Parse faces
        faces = []
        for i in range(n_verts, n_verts + n_faces):
            parts = list(map(int, lines[i].split()))
            n_v_in_face = parts[0]
            if n_v_in_face == 3:
                faces.append((parts[1], parts[2], parts[3]))
            else:
                # Basic triangulation of convex polygon
                for j in range(1, n_v_in_face - 1):
                    faces.append((parts[1], parts[j+1], parts[j+2]))
        
        return TriangleMesh(vertices, faces)

    @staticmethod
    def import_obj(file_path: str) -> TriangleMesh:
        """Imports an OBJ file."""
        from ..mesh import TriangleMesh
        vertices = []
        faces = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if parts[0] == 'v':
                    coords = list(map(float, parts[1:3])) # Only x, y
                    vertices.append(Point(coords[0], coords[1], id=len(vertices)))
                elif parts[0] == 'f':
                    # OBJ indices are 1-based
                    f_indices = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                    if len(f_indices) == 3:
                        faces.append(tuple(f_indices))
                    else:
                        # Triangulate
                        for i in range(1, len(f_indices) - 1):
                            faces.append((f_indices[0], f_indices[i], f_indices[i+1]))
        
        return TriangleMesh(vertices, faces)

    @staticmethod
    def import_stl(file_path: str) -> TriangleMesh:
        """Imports an ASCII STL file."""
        from ..mesh import TriangleMesh
        vertices = []
        faces = []
        point_map = {}
        
        # Simple ASCII STL parser
        with open(file_path, 'r') as f:
            content = f.read().lower()
        
        if 'solid' not in content or 'facet normal' not in content:
            raise ValueError("Binary STL not supported in this simple importer yet. Please provide ASCII STL.")

        lines = content.split('\n')
        current_tri = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('vertex'):
                parts = line.split()
                p = (float(parts[1]), float(parts[2])) # x, y
                if p not in point_map:
                    point_map[p] = len(vertices)
                    vertices.append(Point(p[0], p[1], id=len(vertices)))
                current_tri.append(point_map[p])
                if len(current_tri) == 3:
                    faces.append(tuple(current_tri))
                    current_tri = []
        
        return TriangleMesh(vertices, faces)


class MeshExporter:
    """Exports meshes to various file formats."""

    @staticmethod
    def export_mesh(mesh: TriangleMesh, file_path: str):
        """
        Exports a mesh to a file.
        Detects format based on file extension.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".off":
            MeshExporter.export_off(mesh, file_path)
        elif ext == ".obj":
            MeshExporter.export_obj(mesh, file_path)
        elif ext == ".stl":
            MeshExporter.export_stl(mesh, file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def export_off(mesh: TriangleMesh, file_path: str):
        """Exports a mesh to OFF format."""
        with open(file_path, 'w') as f:
            f.write("OFF\n")
            f.write(f"{len(mesh.vertices)} {len(mesh.faces)} 0\n")
            for v in mesh.vertices:
                f.write(f"{v.x} {v.y} 0.0\n")
            for face in mesh.faces:
                f.write(f"3 {face[0]} {face[1]} {face[2]}\n")

    @staticmethod
    def export_obj(mesh: TriangleMesh, file_path: str):
        """Exports a mesh to OBJ format."""
        with open(file_path, 'w') as f:
            f.write("# Exported by CompGeom\n")
            for v in mesh.vertices:
                f.write(f"v {v.x} {v.y} 0.0\n")
            for face in mesh.faces:
                # OBJ is 1-based
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

    @staticmethod
    def export_stl(mesh: TriangleMesh, file_path: str, solid_name: str = "mesh"):
        """Exports a mesh to ASCII STL format."""
        with open(file_path, 'w') as f:
            f.write(f"solid {solid_name}\n")
            for face in mesh.faces:
                v1, v2, v3 = [mesh.vertices[i] for i in face]
                # Dummy normal (0, 0, 1) for 2D meshes
                f.write("  facet normal 0.0 0.0 1.0\n")
                f.write("    outer loop\n")
                f.write(f"      vertex {v1.x} {v1.y} 0.0\n")
                f.write(f"      vertex {v2.x} {v2.y} 0.0\n")
                f.write(f"      vertex {v3.x} {v3.y} 0.0\n")
                f.write("    endloop\n")
                f.write("  endfacet\n")
            f.write(f"endsolid {solid_name}\n")
