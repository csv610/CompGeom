"""Mesh data structures and topology helpers."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple, Union

from .mesh_base import Mesh, MeshNode, MeshEdge, MeshFace, MeshCell, MeshTopology

mesh_edges = MeshEdge
from .surfmesh.polymesh import PolygonMesh
from .surfmesh.quadmesh import QuadMesh
from .surfmesh.trimesh import TriMesh
from .volmesh.hexmesh import HexMesh
from .volmesh.tetmesh import TetMesh


__all__ = [
    "Mesh",
    "MeshNode",
    "MeshEdge",
    "mesh_edges",
    "MeshFace",
    "MeshCell",
    "MeshTopology",
    "TriMesh",
    "QuadMesh",
    "PolygonMesh",
    "TetMesh",
    "HexMesh",
]
