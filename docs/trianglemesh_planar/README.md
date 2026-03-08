# `trianglemesh.planar`

Purpose:
- lightweight planar subdivision support built around a DCEL-style structure
- point location for polygons with optional holes

Main APIs:
- `build_polygon_dcel(outer_boundary, holes=None)`
- `locate_face(dcel, point)`
- `face_contains_point(face, point)`
- `face_cycle_points(edge)`

Data structures:
- `DCELVertex`
- `DCELHalfEdge`
- `DCELFace`
- `DCEL`

Current scope:
- constructs subdivisions from one outer polygon and zero or more hole cycles
- exposes one bounded face and one exterior face
- point location treats holes as exterior regions

Important limitations:
- not a full general-purpose arrangement/DCEL builder
- does not yet support inserting edges dynamically
- face location currently uses polygon containment rather than a search structure
