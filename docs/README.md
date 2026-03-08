# Module Documentation

This directory contains one `README.md` per Python module in the repository.

Layout:
- `scripts/` contains runnable command-line entry points.
- `src/cli/` contains the command implementations used by those scripts.
- `src/trianglemesh/` contains the reusable implementation package.
- `src/geometry_utils.py`, `src/polygon_utils.py`, and similar files are compatibility shims for legacy imports.
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
