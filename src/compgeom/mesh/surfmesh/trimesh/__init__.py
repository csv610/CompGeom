"""Triangle mesh algorithms (Delaunay and others)."""

from .trimesh import TriMesh
from .delaunay_triangulation import (
    DelaunayMesher,
    triangulate,
    DTriangle,
    MeshTriangle,
)
from .delaunay_dc import triangulate_divide_and_conquer, DivideAndConquerDelaunayMesher
from .delaunay_dynamic import DynamicDelaunay
from .delaunay_constrained import constrained_delaunay_triangulation
from .delaunay_topology import (
    build_topology,
    is_delaunay,
    get_nondelaunay_triangles,
)
from ..platonic_solids import PlatonicSolid
from ..primitives import Primitives
from .domain_mesher import DomainMesher
from compgeom.mesh.surfmesh.node_move_constraints import VertexConstraint

__all__ = [
    "TriMesh",
    "DelaunayMesher",
    "triangulate",
    "DTriangle",
    "MeshTriangle",
    "triangulate_divide_and_conquer",
    "DivideAndConquerDelaunayMesher",
    "DynamicDelaunay",
    "constrained_delaunay_triangulation",
    "build_topology",
    "is_delaunay",
    "get_nondelaunay_triangles",
    "PlatonicSolid",
    "Primitives",
    "DomainMesher",
    "VertexConstraint",
]
