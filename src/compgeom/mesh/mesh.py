"""Mesh data structures and topology helpers."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple, Union

from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshEdge, MeshFace, MeshCell, MeshTopology
from compgeom.mesh.mesh_affine_transform import MeshAffineTransform
from compgeom.mesh.mesh_geometry import MeshGeometry

mesh_edges = MeshEdge
from compgeom.mesh.surfmesh.polymesh import PolygonMesh
from compgeom.mesh.surfmesh.quadmesh import QuadMesh
from compgeom.mesh.surfmesh.trimesh import TriMesh
from compgeom.mesh.volmesh.hexmesh import HexMesh
from compgeom.mesh.volmesh.tetmesh import TetMesh

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
