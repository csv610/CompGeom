"""Shared geometry and algorithm package for the TriMesh project."""

# 1. Package access
from compgeom import kernel as geometry
from compgeom import mesh
from compgeom import polygon
from compgeom import algo
from compgeom import graphics
from compgeom import algebraic

# 2. Flattened API - Foundations
from compgeom.kernel import *

# 3. Flattened API - Shapes and Basic Algos
from compgeom.algo.bounding import *
from compgeom.algo.lower_envelop import *
from compgeom.algo.path import *
from compgeom.algo.point_trees import *
from compgeom.algo.points_sampling import *
from compgeom.algo.proximity import *
from compgeom.algo.random_walker import *
from compgeom.algo.rectangle_packing import *
from compgeom.algo.shapes import *

# 4. Flattened API - Graphics
from compgeom.graphics.visualization import *

# 5. Flattened API - Mesh
from compgeom.mesh import *

# 6. Flattened API - Polygon
from compgeom.polygon import *

# Build comprehensive __all__
import sys

__all__ = [name for name in dir() if not name.startswith("_") and name not in ["sys"]]
