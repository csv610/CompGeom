"""Shared geometry and algorithm package for the TriangleMesh project."""

# 1. Package access
from . import kernel as geometry
from . import mesh
from . import polygon
from . import algo
from . import graphics

# 2. Flattened API - Foundations
from .kernel import *

# 3. Flattened API - Shapes and Basic Algos
from .algo.bounding import *
from .algo.lower_envelop import *
from .algo.path import *
from .algo.point_trees import *
from .algo.points_sampling import *
from .algo.proximity import *
from .algo.random_walker import *
from .algo.rectangle_packing import *
from .algo.shapes import *
from .algo.space_filling_curves import *

# 4. Flattened API - Graphics
from .graphics.visualization import *

# 5. Flattened API - Mesh
from .mesh import *

# 6. Flattened API - Polygon
from .polygon import *

# Build comprehensive __all__
import sys
__all__ = [name for name in dir() if not name.startswith('_') and name not in ['sys']]
