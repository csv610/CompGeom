"""Triangle mesh algorithms (Delaunay and others)."""

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
from .platonic_solids import PlatonicSolid
from .domain_mesher import DomainMesher

__all__ = [
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
    "DomainMesher",
]
