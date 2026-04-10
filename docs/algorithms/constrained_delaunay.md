# Constrained Delaunay Triangulation (CDT)

Constrained Delaunay Triangulation is a version of Delaunay triangulation that forces certain edges (constraints) into the triangulation. It is essential for representing domains with specific boundaries, holes, or internal features that must be preserved.

## Overview

While a standard Delaunay triangulation maximizes the minimum angle and satisfies the "empty circumcircle" property for all points, it may not respect the boundaries of a non-convex polygon. CDT modifies the Delaunay criteria to ensure that all constraint edges are present in the final mesh, while maintaining the Delaunay property for all other edges as much as possible.

## Implementation Details

In `CompGeom`, the CDT is implemented using an iterative edge-flip approach:
1.  **Initial Triangulation**: The domain (including holes) is initially triangulated using a standard polygon triangulation algorithm.
2.  **Constraint Enforcement**: Bridge edges are added to connect holes to the outer boundary, creating a single degenerate polygon that is then triangulated.
3.  **Edge Flipping**: All internal edges that are not part of the constraints are placed in a queue. Edges are flipped if they violate the Delaunay condition, provided the flip doesn't cross a constraint and maintains the domain's validity.

## Usage

```python
from compgeom.mesh import constrained_delaunay_triangulation
from compgeom import Point2D

# Define outer boundary
outer = [Point2D(0,0), Point2D(10,0), Point2D(10,10), Point2D(0,10)]

# Define holes
holes = [[Point2D(4,4), Point2D(6,4), Point2D(6,6), Point2D(4,6)]]

triangles, constrained_edges = constrained_delaunay_triangulation(outer, holes)
```

## References
- Chew, L. Paul. "Constrained Delaunay Triangulations." Algorithmica, 1989.
- Sloan, S. W. "A Fast Algorithm for Generating Constrained Delaunay Triangulations." Computers & Structures, 1993.
