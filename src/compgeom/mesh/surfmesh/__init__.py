"""Surface mesh processing and primitive generation."""

from .platonic_solids import PlatonicSolid
from .trimesh.primitives import Primitives

__all__ = [
    "PlatonicSolid",
    "Primitives",
]
