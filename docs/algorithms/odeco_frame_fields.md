# Odeco Frame Fields

Odeco Frame Fields is a method for designing 3D anisotropic frame fields in tetrahedral meshes using Orthonormal Decomposable (Odeco) tensors.

## Overview

A frame field is a volumetric structure that assigns a 3D orthogonal frame to each point in a volume. Frame fields are essential for generating high-quality quad-dominant or hex-dominant meshes. Standard frame field representations (like 4th-order tensors) can be difficult to control. The Odeco representation provides a more direct way to specify the orientation and stretching of the local frame.

## Implementation Details

The `OdecoFrameField` implementation in `CompGeom` allows for:
1.  **Boundary Alignment**: The frames can be explicitly aligned to boundary normals.
2.  **Anisotropy Control**: The stretching magnitudes along each frame axis can be specified.
3.  **Smoothness Optimization**: The orientations and stretching can be propagated through the volume via a smoothing process.

## Usage

```python
from compgeom.mesh.volume.odeco_frame_field import OdecoFrameField
from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh
import numpy as np

# Load a tetrahedral mesh
mesh = TetMesh.from_file("volume.obj")

# Initialize and align to boundary
off = OdecoFrameField(mesh)
off.align_to_boundary(normals, indices)

# Propagate across the volume
off.solve_smoothness(iterations=10)
```

## References
- Zhu, Y., et al. "Designing 3D Anisotropic Frame Fields with Odeco Tensors." ACM Transactions on Graphics (SIGGRAPH), 2025.
- Panozzo, D., et al. "Frame Fields: An Orientation-aware Surface Representation." ACM Transactions on Graphics (SIGGRAPH), 2014.
