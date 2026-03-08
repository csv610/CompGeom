# Module Documentation

This directory contains one `README.md` per Python module in the repository.

Layout:
- `cli/` contains the concrete command-line entry point implementations.
- root-level CLI files are thin compatibility stubs that delegate into `cli/`.
- `trianglemesh/` contains the reusable implementation package.
- `docs/<module_name>/README.md` documents root-level scripts and compatibility modules.
- `docs/trianglemesh_<module_name>/README.md` documents implementation modules under `trianglemesh/`.

Each README describes:
- purpose
- main algorithm or data structure
- expected input/output shape
- important limitations or assumptions

Start here for the main implementation modules:
- `trianglemesh_geometry`
- `trianglemesh_polygon`
- `trianglemesh_proximity`
- `trianglemesh_triangulation`
- `trianglemesh_spatial`
- `trianglemesh_walks`
- `trianglemesh_bounding`
- `trianglemesh_mesh`
