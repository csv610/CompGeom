"""Generation of common geometric primitive meshes."""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, List, Tuple

from compgeom.kernel import Point3D
from compgeom.mesh.surfmesh.platonic_solids import PlatonicSolid

if TYPE_CHECKING:
    from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh

class Primitives:
    """Generates meshes for common geometric primitives."""

    @staticmethod
    def _create_mesh(vertices: List[Point3D], faces: List[Tuple[int, int, int]]) -> TriMesh:
        from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh
        return TriMesh(vertices, faces)

    @staticmethod
    def sphere(radius: float = 1.0, subdivisions: int = 3) -> TriMesh:
        """Generates an isotropic sphere mesh using icosahedron subdivision."""
        from compgeom.mesh.surfmesh.trimesh.mesh_refinement import TriMeshRefiner
        mesh = PlatonicSolid.icosahedron(size=1.0)
        
        for _ in range(subdivisions):
            mesh = TriMeshRefiner.subdivide_linear(mesh)
            
        # Project to sphere
        new_vertices = []
        for v in mesh.vertices:
            length = math.sqrt(v.x**2 + v.y**2 + v.z**2)
            if length > 0:
                new_v = Point3D(v.x / length * radius, v.y / length * radius, v.z / length * radius, id=v.id)
                new_vertices.append(new_v)
            else:
                new_vertices.append(v)
        
        return Primitives._create_mesh(new_vertices, mesh.faces)

    @staticmethod
    def ellipsoid(rx: float = 1.0, ry: float = 1.0, rz: float = 1.0, subdivisions: int = 3) -> TriMesh:
        """Generates an isotropic ellipsoid mesh."""
        mesh = Primitives.sphere(radius=1.0, subdivisions=subdivisions)
        
        new_vertices = []
        for v in mesh.vertices:
            new_v = Point3D(v.x * rx, v.y * ry, v.z * rz, id=v.id)
            new_vertices.append(new_v)
        
        return Primitives._create_mesh(new_vertices, mesh.faces)

    @staticmethod
    def oblate_spheroid(equatorial_radius: float = 1.0, polar_radius: float = 0.8, subdivisions: int = 3) -> TriMesh:
        """Generates an oblate spheroid mesh (flattened sphere)."""
        if polar_radius > equatorial_radius:
            raise ValueError("For an oblate spheroid, equatorial_radius must be greater than polar_radius.")
        return Primitives.ellipsoid(rx=equatorial_radius, ry=equatorial_radius, rz=polar_radius, subdivisions=subdivisions)

    @staticmethod
    def prolate_spheroid(equatorial_radius: float = 0.8, polar_radius: float = 1.0, subdivisions: int = 3) -> TriMesh:
        """Generates a prolate spheroid mesh (stretched sphere)."""
        if polar_radius < equatorial_radius:
            raise ValueError("For a prolate spheroid, polar_radius must be greater than equatorial_radius.")
        return Primitives.ellipsoid(rx=equatorial_radius, ry=equatorial_radius, rz=polar_radius, subdivisions=subdivisions)

    @staticmethod
    def torus(major_radius: float = 1.0, minor_radius: float = 0.3, major_segments: int = 32, minor_segments: int = 16) -> TriMesh:
        """Generates a torus mesh."""
        vertices = []
        for i in range(major_segments + 1):
            u = 2.0 * math.pi * i / major_segments
            for j in range(minor_segments + 1):
                v = 2.0 * math.pi * j / minor_segments
                x = (major_radius + minor_radius * math.cos(v)) * math.cos(u)
                y = (major_radius + minor_radius * math.cos(v)) * math.sin(u)
                z = minor_radius * math.sin(v)
                vertices.append(Point3D(x, y, z, id=len(vertices)))

        faces = []
        for i in range(major_segments):
            for j in range(minor_segments):
                v0 = i * (minor_segments + 1) + j
                v1 = v0 + 1
                v2 = (i + 1) * (minor_segments + 1) + j
                v3 = v2 + 1
                # Outward normals: (v0, v2, v1) and (v1, v2, v3)
                faces.append((v0, v2, v1))
                faces.append((v1, v2, v3))
        return Primitives._create_mesh(vertices, faces)

    @staticmethod
    def cube(size: float = 1.0) -> TriMesh:
        """Generates a regular cube mesh."""
        return PlatonicSolid.cube(size)

    @staticmethod
    def cuboid(length: float = 1.0, width: float = 1.0, height: float = 1.0) -> TriMesh:
        """Generates a cuboid (rectangular prism) mesh."""
        l = length / 2.0
        w = width / 2.0
        h = height / 2.0
        v = [
            Point3D(-l, -w, -h, id=0), Point3D(l, -w, -h, id=1),
            Point3D(l, w, -h, id=2), Point3D(-l, w, -h, id=3),
            Point3D(-l, -w, h, id=4), Point3D(l, -w, h, id=5),
            Point3D(l, w, h, id=6), Point3D(-l, w, h, id=7)
        ]
        f = [
            (0, 3, 2), (0, 2, 1), (4, 5, 6), (4, 6, 7),
            (0, 1, 5), (0, 5, 4), (2, 3, 7), (2, 7, 6),
            (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5)
        ]
        return Primitives._create_mesh(v, f)

    @staticmethod
    def quad(width: float = 1.0, height: float = 1.0) -> TriMesh:
        """Generates a planar quad (rectangle) mesh in the XY plane."""
        w2 = width / 2.0
        h2 = height / 2.0
        vertices = [
            Point3D(-w2, -h2, 0.0, id=0),
            Point3D(w2, -h2, 0.0, id=1),
            Point3D(w2, h2, 0.0, id=2),
            Point3D(-w2, h2, 0.0, id=3)
        ]
        faces = [(0, 1, 2), (0, 2, 3)]
        return Primitives._create_mesh(vertices, faces)

    @staticmethod
    def polygon(radius: float = 1.0, segments: int = 32) -> TriMesh:
        """Generates a planar regular n-gon mesh in the XY plane."""
        vertices = [Point3D(0.0, 0.0, 0.0, id=0)]
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            vertices.append(Point3D(radius * math.cos(angle), radius * math.sin(angle), 0.0, id=i+1))

        faces = []
        for i in range(segments):
            v1 = 1 + i
            v2 = 1 + (i + 1) % segments
            faces.append((0, v1, v2))

        return Primitives._create_mesh(vertices, faces)

    @staticmethod
    def cylinder(radius: float = 1.0, height: float = 1.0, segments: int = 32, height_segments: int = 1) -> TriMesh:
        """Generates a cylinder mesh."""
        vertices = []
        h_half = height / 2.0
        
        # Vertices for each ring
        for j in range(height_segments + 1):
            z = -h_half + j * height / height_segments
            for i in range(segments):
                angle = 2.0 * math.pi * i / segments
                vertices.append(Point3D(radius * math.cos(angle), radius * math.sin(angle), z, id=len(vertices)))
        
        # Center points for caps
        center_bottom_idx = len(vertices)
        vertices.append(Point3D(0, 0, -h_half, id=center_bottom_idx))
        center_top_idx = len(vertices)
        vertices.append(Point3D(0, 0, h_half, id=center_top_idx))

        faces = []
        # Side faces
        for j in range(height_segments):
            for i in range(segments):
                v0 = j * segments + i
                v1 = j * segments + (i + 1) % segments
                v2 = (j + 1) * segments + i
                v3 = (j + 1) * segments + (i + 1) % segments
                faces.append((v0, v1, v3))
                faces.append((v0, v3, v2))
        
        # Bottom cap faces
        for i in range(segments):
            faces.append((center_bottom_idx, (i + 1) % segments, i))
        
        # Top cap faces
        top_offset = height_segments * segments
        for i in range(segments):
            faces.append((center_top_idx, top_offset + i, top_offset + (i + 1) % segments))

        return Primitives._create_mesh(vertices, faces)

    @staticmethod
    def hexagonal_prism(radius: float = 1.0, height: float = 1.0, height_segments: int = 1) -> TriMesh:
        """Generates a hexagonal prism mesh."""
        return Primitives.cylinder(radius, height, segments=6, height_segments=height_segments)

    @staticmethod
    def triangular_prism(radius: float = 1.0, height: float = 1.0, height_segments: int = 1) -> TriMesh:
        """Generates a triangular prism mesh."""
        return Primitives.cylinder(radius, height, segments=3, height_segments=height_segments)

    @staticmethod
    def cone(radius: float = 1.0, height: float = 1.0, segments: int = 32, height_segments: int = 1) -> TriMesh:
        """Generates a cone mesh."""
        vertices = []
        h_half = height / 2.0
        
        # Tip
        tip_idx = 0
        vertices.append(Point3D(0, 0, h_half, id=tip_idx))
        
        # Vertices for each ring from top to bottom (excluding tip)
        for j in range(1, height_segments + 1):
            ratio = j / height_segments
            z = h_half - ratio * height
            r = ratio * radius
            for i in range(segments):
                angle = 2.0 * math.pi * i / segments
                vertices.append(Point3D(r * math.cos(angle), r * math.sin(angle), z, id=len(vertices)))
        
        # Base center
        base_center_idx = len(vertices)
        vertices.append(Point3D(0, 0, -h_half, id=base_center_idx))

        faces = []
        # Tip faces
        for i in range(segments):
            v1 = 1 + i
            v2 = 1 + (i + 1) % segments
            faces.append((tip_idx, v1, v2))
            
        # Side ring faces
        for j in range(height_segments - 1):
            for i in range(segments):
                v0 = 1 + j * segments + i
                v1 = 1 + j * segments + (i + 1) % segments
                v2 = 1 + (j + 1) * segments + i
                v3 = 1 + (j + 1) * segments + (i + 1) % segments
                faces.append((v0, v1, v3))
                faces.append((v0, v3, v2))
        
        # Base faces
        base_offset = 1 + (height_segments - 1) * segments
        for i in range(segments):
            v1 = base_offset + i
            v2 = base_offset + (i + 1) % segments
            faces.append((base_center_idx, v2, v1))

        return Primitives._create_mesh(vertices, faces)

    @staticmethod
    def pyramid(base_size: float = 1.0, height: float = 1.0, base_segments: int = 4, height_segments: int = 1) -> TriMesh:
        """Generates a pyramid mesh with a regular n-gon base."""
        # Radius such that the side length of the base n-gon is base_size
        radius = base_size / (2.0 * math.sin(math.pi / base_segments))
        return Primitives.cone(radius, height, segments=base_segments, height_segments=height_segments)

    @staticmethod
    def tetrahedron(size: float = 1.0) -> TriMesh:
        """Generates a regular tetrahedron mesh."""
        return PlatonicSolid.tetrahedron(size)

    @staticmethod
    def octahedron(size: float = 1.0) -> TriMesh:
        """Generates a regular octahedron mesh."""
        return PlatonicSolid.octahedron(size)

    @staticmethod
    def dodecahedron(size: float = 1.0) -> TriMesh:
        """Generates a regular dodecahedron mesh."""
        return PlatonicSolid.dodecahedron(size)

    @staticmethod
    def icosahedron(size: float = 1.0) -> TriMesh:
        """Generates a regular icosahedron mesh."""
        return PlatonicSolid.icosahedron(size)
