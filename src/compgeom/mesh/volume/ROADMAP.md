# Computational Geometry Mesh Library Roadmap

This roadmap tracks the implementation of advanced mesh algorithms missing from the current codebase.

## Phase 1: Surface Reconstruction
- [x] **Ball Pivoting Algorithm (BPA):** Direct triangulation by "rolling" a ball over points.
- [x] **Poisson Surface Reconstruction:** Watertight implicit surface reconstruction from noisy point clouds.

## Phase 2: Shape Analysis & Skeletonization
- [x] **Shape Diameter Function (SDF):** Local thickness measurement at mesh points.
- [x] **L1-Medial Skeleton:** Robust 1D topological skeleton extraction.

## Phase 3: Mesh Deformation
- [x] **As-Rigid-As-Possible (ARAP):** Natural mesh editing with local feature preservation.
- [x] **Cage-based Deformation:** Harmonic and Mean Value Coordinates for low-poly cage control.

## Phase 4: Spectral Geometry
- [x] **Laplace-Beltrami Operator:** Eigen-decomposition and spectral analysis.
- [x] **Heat Kernel Signature (HKS):** Intrinsic shape descriptors for non-rigid matching.

## Phase 5: Advanced Remeshing
- [x] **Field-aligned Quad Remeshing:** Cross-field optimization for structured quad guidance.
- [ ] **Anisotropic Remeshing:** Alignment with principal curvature directions.

## Phase 6: Volume Mesh Optimization
- [ ] **Sliver Removal:** Topological reconnection to eliminate degenerate tetrahedra.
- [x] **Dihedral Angle Smoothing:** Variational improvement of TetMesh quality (Laplacian smoothing).

## Phase 7: Physical Modeling Support
- [x] **Quadratic (P2) Elements:** Conversion of linear Tet4/Tri3 to quadratic Tet10/Tri6.
- [ ] **Boundary Layer Meshing:** Specialized stretched elements for CFD.

## Phase 8: UV Mapping & Texturing
- [ ] **UV Atlas Generation:** Automatic segmentation of meshes into chart groups.
- [ ] **UV Packing:** Efficient layout of UV islands into texture space.

## Phase 9: Modern Era (SIGGRAPH 2020+ & SoCG 2025)
- [x] **Neural SDF Fitting:** Representing surfaces via continuous neural fields.
- [x] **The Vector Heat Method:** Robust geodesics and parallel transport.
- [x] **3D Gaussian Splatting:** Point-based differentiable rendering (Foundation).
- [x] **Linear Time Maximum Overlap (SoCG 2025):** $O(n)$ optimal translation for convex polygons.
- [ ] **Incremental Potential Contact (IPC):** Intersection-free simulation (Skipped by user).



