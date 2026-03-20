"""Mesh data structures and topology helpers."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple, Union

from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshEdge, MeshFace, MeshCell
from compgeom.mesh.mesh_topology import MeshTopology, mesh_neighbors, get_mesh_edges
from compgeom.mesh.mesh_affine_transform import MeshAffineTransform
from compgeom.mesh.mesh_geometry import MeshGeometry

mesh_edges = get_mesh_edges
from compgeom.mesh.surface.polygon.polygon import PolygonMesh
from compgeom.mesh.surface.quadmesh.quadmesh import QuadMesh
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.mesh.volume.hexmesh.hexmesh import HexMesh
from compgeom.mesh.volume.hexmesh.conforming_generator import ConformingHexMesher
from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh

__all__ = [
    "Mesh",
    "MeshNode",
    "MeshEdge",
    "MeshFace",
    "MeshCell",
    "mesh_edges",
    "MeshTopology",
    "mesh_neighbors",
    "MeshAffineTransform",
    "MeshGeometry",
    "TriMesh",
    "QuadMesh",
    "PolygonMesh",
    "SurfaceMesh",
    "TetMesh",
    "HexMesh",
    "ConformingHexMesher",
]
