# `trianglemesh/polygon.py`

Purpose: reusable polygon algorithms and polygon generators.

Algorithms:
- area, centroid, and orientation via the shoelace formula
- point-in-polygon via ray casting plus edge checks
- ear clipping triangulation
- hole triangulation by bridge insertion plus ear clipping
- art-gallery guard placement by 3-coloring a triangulation
- Hertel-Mehlhorn style convex partitioning
- visibility polygon computation from an interior viewpoint
- shortest path inside a simple polygon via a visibility graph
- convex hulls via Graham scan and monotone chain
- random convex/simple polygon generation
- uniform triangle sampling via reflected barycentric coordinates

Inputs: lists of `Point` objects in boundary order.

Outputs: scalars, polygon lists, triangle index lists, or generated samples depending on the function.

Assumptions: many routines expect simple polygons.
