# Winding-Filtered Tetrahedral Meshing

Winding-Filtered Tetrahedral Meshing is a robust technique for generating a volumetric tetrahedral mesh from a surface mesh, even if the surface mesh is "dirty" (i.e., contains self-intersections or holes).

## Overview

Traditional tetrahedralization algorithms (like constrained Delaunay) often require a clean, manifold surface. In contrast, winding-filtered meshing uses the Generalized Winding Number (GWN) to classify tetrahedra as interior or exterior, which is robust even for non-manifold inputs.

## Implementation Details

In `CompGeom`, the `WindingFilteredTetMesher` uses the following process (inspired by fTetWild):
1.  **Bounding Box Expansion**: Create a large super-tetrahedron containing the entire surface mesh.
2.  **Point Insertion**: Add surface vertices and a dense grid of internal Steiner points to the tetrahedralization.
3.  **Delaunay Tetrahedralization**: Construct a global Delaunay tetrahedralization of the point set.
4.  **Winding-Based Filtering**: For each tetrahedron, compute the Generalized Winding Number of its centroid with respect to the original surface mesh.
5.  **Output**: Retain only tetrahedra where the GWN $> 0.5$ (indicating the interior of the domain).

## Usage

```python
from compgeom.mesh.volume.tetmesh.winding_filtered_mesher import WindingFilteredTetMesher
import numpy as np

# surface vertices and faces as numpy arrays
vertices = np.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1]])
faces = np.array([[0,1,2], [0,2,3], [0,3,1], [1,2,3]])

mesher = WindingFilteredTetMesher(vertices, faces)
tet_mesh = mesher.mesh(refinement_factor=1.0)
```

## References
- Hu, Y., et al. "fTetWild: Robust Tetrahedral Meshing in the Wild." ACM Transactions on Graphics (SIGGRAPH), 2018.
- Jacobson, A., et al. "Robust Inside-Outside Segmentation using Generalized Winding Numbers." ACM Transactions on Graphics (SIGGRAPH), 2013.
