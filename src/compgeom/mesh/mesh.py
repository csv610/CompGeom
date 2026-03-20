"""Mesh data structures and topology helpers."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple, Union

from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshEdge, MeshFace, MeshCell, MeshTopology
from compgeom.mesh.mesh_affine_transform import MeshAffineTransform
from compgeom.mesh.mesh_geometry import MeshGeometry

mesh_edges = MeshEdge
from compgeom.mesh.surface.polygon import PolygonMesh
from compgeom.mesh.surface.quadmesh import QuadMesh
from compgeom.mesh.surface.trimesh import TriMesh
from compgeom.mesh.volume.hexmesh import HexMesh
from compgeom.mesh.volume.tetmesh import TetMesh

__all__ = [
    "Mesh",
    "MeshNode",
    "MeshEdge",
    "MeshFace",
    "MeshCell",
    "mesh_edges",
    "MeshTopology",
    "MeshAffineTransform",
    "MeshGeometry",
    "TriMesh",
    "QuadMesh",
    "PolygonMesh",
    "TetMesh",
    "HexMesh",
]
