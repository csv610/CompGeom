import os
import sys
import pytest
from pathlib import Path

_THIRDPARTY_OPENVDB = (
    Path(__file__).parent.parent
    / "3rdparty"
    / "openvdb"
    / "build"
    / "openvdb"
    / "openvdb"
)
_openvdb_dylib = _THIRDPARTY_OPENVDB / "libopenvdb.dylib"
if _openvdb_dylib.exists():
    _lib_path = str(_THIRDPARTY_OPENVDB)
    if sys.platform == "darwin":
        if "DYLD_LIBRARY_PATH" in os.environ:
            os.environ["DYLD_LIBRARY_PATH"] = (
                _lib_path + ":" + os.environ["DYLD_LIBRARY_PATH"]
            )
        else:
            os.environ["DYLD_LIBRARY_PATH"] = _lib_path
    else:
        if "LD_LIBRARY_PATH" in os.environ:
            os.environ["LD_LIBRARY_PATH"] = (
                _lib_path + ":" + os.environ["LD_LIBRARY_PATH"]
            )
        else:
            os.environ["LD_LIBRARY_PATH"] = _lib_path

    try:
        import openvdb
    except ImportError:
        pass

import compgeom.mesh.mesh
from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshFace, MeshCell
from compgeom.mesh.mesh_topology import MeshTopology
from compgeom.mesh.mesh_geometry import MeshGeometry
from compgeom.mesh.algorithms.mesh_reordering import MeshReorderer


def patch_mesh_classes():
    def face_iter(self):
        return iter(self.v_indices)

    def face_getitem(self, idx):
        return self.v_indices[idx]

    def face_len(self):
        return len(self.v_indices)

    def face_eq(self, other):
        if isinstance(other, tuple):
            return self.v_indices == other
        if isinstance(other, (MeshFace, MeshCell)):
            return self.id == other.id and self.v_indices == other.v_indices
        return False

    def face_hash(self):
        return hash(self.v_indices)

    MeshFace.__iter__ = face_iter
    MeshFace.__getitem__ = face_getitem
    MeshFace.__len__ = face_len
    MeshFace.__eq__ = face_eq
    MeshFace.__hash__ = face_hash

    MeshCell.__iter__ = face_iter
    MeshCell.__getitem__ = face_getitem
    MeshCell.__len__ = face_len
    MeshCell.__eq__ = face_eq
    MeshCell.__hash__ = face_hash

    @property
    def topology(self):
        return MeshTopology(self)

    Mesh.topology = topology

    @property
    def centroid(self):
        return MeshGeometry.centroid(self)

    Mesh.centroid = centroid

    def bounding_box_method(self):
        return MeshGeometry.bounding_box(self)

    Mesh.bounding_box = bounding_box_method

    def is_watertight(self):
        return MeshTopology(self).is_watertight()

    Mesh.is_watertight = is_watertight

    def reorder_nodes(self, new_indices):
        MeshReorderer.reorder_nodes(self, new_indices)

    Mesh.reorder_nodes = reorder_nodes

    @property
    def elements(self):
        return self.faces if self.faces else self.cells

    Mesh.elements = elements


patch_mesh_classes()
