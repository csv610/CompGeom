import math
import random
import tempfile
from io import StringIO
from pathlib import Path

import pytest

from compgeom import Point2D, Point3D, minimum_bounding_box, minimum_enclosing_circle
from compgeom.cli import _shared as cli_shared
from compgeom.cli import line_arrangement_cli as line_cli
from compgeom.cli import reflection_polygon_cli as reflection_cli
from compgeom.cli.polygon_boolean_operations_cli import (
    build_boundary_segments,
    centroid,
    deduplicate_polygons,
    format_point as boolean_format_point,
    handle_no_intersection_case,
    parse_polygon,
    point_on_segment,
    point_key as boolean_point_key,
    polygon_edges,
    polygon_key,
    representative_point,
    segment_intersection_points,
    split_polygon_edges_against_other,
    trace_directed_loops,
)
from compgeom.algo.lower_envelop import DavenportSchinzel
from compgeom.algo.points_sampling import (
    PointSampler,
    generate_points_in_circle,
    generate_points_in_rectangle,
)
from compgeom.algo.point_trees import PointQuadtree, PointSimplifier, build_kdtree, display_kdtree
from compgeom.algo.proximity import (
    ClosestPair,
    LargestEmptyCircle,
    do_intersect,
    farthest_pair,
    minkowski_sum,
    welzl,
)
from compgeom.algo.random_walker import (
    RandomWalker,
    generate_spiral_path,
    generate_zigzag_path,
    simulate_random_walk_2d,
    simulate_random_walk_3d,
    simulate_saw_2d,
)
from compgeom.algo.rectangle_packing import RectanglePacker
from compgeom.algo.space_filling_curves import SpaceFillingCurves
from compgeom.algo.shapes import (
    Circle,
    Cuboid,
    Hexahedron,
    LineSegment,
    Plane,
    Ray,
    Rectangle,
    Sphere,
    Square,
    Tetrahedron,
    Triangle,
)
from compgeom.graphics.geo_plot import GeomPlot
from compgeom.graphics.visualization import generate_svg_path, save_png, save_svg
from compgeom.mesh import CuthillMcKee, MeshColoring, MeshTransfer, PolygonMesh, QuadMesh, TriangleMesh, VoronoiDiagram
from compgeom.mesh.delaunay_triangulation import (
    DTriangle,
    DelaunayMesher,
    DynamicDelaunay,
    MeshTriangle,
    build_topology,
    get_nondelaunay_triangles,
    is_delaunay,
    triangulate,
)
from compgeom.mesh.mesh_io import MeshImporter, MeshExporter, OBJFileHandler, OFFFileHandler, STLFileHandler
from compgeom.mesh.surfmesh.trimesh.mesh_refinement import TriMeshRefiner
from compgeom.mesh.surfmesh.quadmesh.simple_tri2quads import TriangleToQuadConverter
from compgeom.mesh.volmesh.voxelmesh.voxelization import MeshVoxelizer
from compgeom.polygon.circle_packing import CirclePacker
from compgeom.polygon.distance_map import DistanceMapSolver
from compgeom.polygon.polygon_generator import PolygonGenerator
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_smoothing import PolygonalMeanCurvatureFlow


def test_minimum_enclosing_shapes_handle_degenerate_inputs():
    center, radius = minimum_enclosing_circle([])
    assert center == Point2D(0, 0)
    assert radius == 0.0

    single = minimum_bounding_box([Point2D(2, 3)])
    assert single["area"] == 0.0
    assert single["center"] == Point2D(2, 3)
    assert len(single["corners"]) == 4

    segment = minimum_bounding_box([Point2D(0, 0), Point2D(4, 0)])
    assert segment["area"] == 0.0
    assert math.isclose(segment["width"], 4.0, abs_tol=1e-9)
    assert segment["height"] == 0.0


def test_davenport_schinzel_envelope_and_sequence_cover_crossing_segments():
    segments = [
        (Point2D(0, 3), Point2D(4, -1)),
        (Point2D(0, 0), Point2D(4, 2)),
        (Point2D(2, -1), Point2D(2, 3)),
    ]

    envelope = DavenportSchinzel.lower_envelope_segments(segments)
    sequence = DavenportSchinzel.calculate_sequence(segments)

    assert len(envelope) == 2
    assert sequence == [1, 0]
    assert envelope[0].x_start == 0.0
    assert math.isclose(envelope[0].x_end, 2.0, abs_tol=1e-9)
    assert math.isclose(envelope[1].x_start, 2.0, abs_tol=1e-9)
    assert envelope[1].x_end == 4.0


def test_rectangle_packer_supports_empty_square_and_svg_visualization():
    assert RectanglePacker.pack([]) == (0, 0, [])

    width, height, placements = RectanglePacker.pack([(3, 1), (2, 2), (1, 4)], target_shape="square")
    svg = RectanglePacker.visualize(width, height, placements, cell_size=10)

    assert placements
    assert max(width, height) <= sum(rect.width for rect in placements)
    assert svg.startswith('<svg width="')
    for rect in placements:
        assert f">{rect.id}</text>" in svg


def test_point_sampler_helpers_generate_points_in_expected_domains():
    random.seed(7)

    disk_points = PointSampler.in_circle(Point2D(1, -1), 2.0, n_points=5)
    circle_points = PointSampler.on_circle(Point2D(0, 0), 3.0, n_points=5)
    rect_points = PointSampler.on_rectangle(6.0, 4.0, n_points=6, center=Point2D(1, 2))
    line_points = PointSampler.on_line_segment(Point2D(0, 0), Point2D(2, 2), n_points=4)
    cube_points = PointSampler.in_cube(2.0, n_points=4, center=Point3D(1, 1, 1))
    sphere_points = PointSampler.on_sphere(Point3D(0, 0, 0), 2.0, n_points=8)

    assert len(generate_points_in_circle(Point2D(0, 0), 1.0, 3)) == 3
    assert len(generate_points_in_rectangle(2.0, 4.0, 3, Point2D(1, 1))) == 3
    assert len(disk_points) == 5
    assert len(circle_points) == 5
    assert len(rect_points) == 6
    assert len(line_points) == 4
    assert len(cube_points) == 4
    assert len(sphere_points) > 0

    for point in disk_points:
        assert math.hypot(point.x - 1.0, point.y + 1.0) <= 2.0 + 1e-9
    for point in circle_points:
        assert math.isclose(math.hypot(point.x, point.y), 3.0, rel_tol=1e-6, abs_tol=1e-6)
    for point in rect_points:
        on_vertical = math.isclose(point.x, -2.0, abs_tol=1e-9) or math.isclose(point.x, 4.0, abs_tol=1e-9)
        on_horizontal = math.isclose(point.y, 0.0, abs_tol=1e-9) or math.isclose(point.y, 4.0, abs_tol=1e-9)
        assert on_vertical or on_horizontal
    for point in line_points:
        assert math.isclose(point.x, point.y, abs_tol=1e-9)
        assert 0.0 <= point.x <= 2.0
    for point in cube_points:
        assert 0.0 <= point.x <= 2.0
        assert 0.0 <= point.y <= 2.0
        assert 0.0 <= point.z <= 2.0
    for point in sphere_points:
        assert math.isclose(math.sqrt(point.x**2 + point.y**2 + point.z**2), 2.0, rel_tol=1e-6, abs_tol=1e-6)


def test_mesh_coloring_reordering_and_voronoi_diagram_helpers():
    vertices = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1), Point2D(1, 1)]
    mesh = TriangleMesh(vertices, [(0, 1, 2), (1, 3, 2)])

    element_colors = MeshColoring.color_elements(mesh)
    vertex_colors = MeshColoring.color_vertices(mesh)
    vertex_order = CuthillMcKee.reorder_vertices(mesh, reverse=False)
    element_order = CuthillMcKee.reorder_elements(mesh, reverse=False)

    assert element_colors[0] != element_colors[1]
    assert vertex_colors[1] != vertex_colors[2]
    assert sorted(vertex_order) == [0, 1, 2, 3]
    assert sorted(element_order) == [0, 1]

    diagram = VoronoiDiagram()
    empty_mesh = diagram.compute([])
    assert empty_mesh.vertices == []
    assert empty_mesh.elements == []

    circle_boundary = VoronoiDiagram.get_circle_boundary(radius=2.0, center=(1.0, -1.0), n_segments=8)
    square_boundary = VoronoiDiagram.get_square_boundary(size=4.0, center=(1.0, -1.0))
    assert len(circle_boundary) == 8
    assert len(square_boundary) == 4

    result = diagram.compute([Point2D(0, 0, 0), Point2D(2, 0, 1)], boundary_type="circle")
    assert len(diagram.cells) == 2
    assert result.vertices
    assert result.elements


def test_proximity_helpers_cover_intersections_pairs_and_minkowski_sum():
    points = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), Point2D(1, 1.1)]

    dist, pair = ClosestPair.divide_and_conquer(points)
    assert math.isclose(dist, math.hypot(1.0, 0.9), abs_tol=1e-9)
    assert set(pair) == {Point2D(2, 2), Point2D(1, 1.1)}

    stream_dist, stream_pair = ClosestPair.grid_based_massive(iter(points), sample_size=3)
    assert math.isclose(stream_dist, dist, abs_tol=1e-9)
    assert Point2D(1, 1.1) in set(stream_pair)

    assert do_intersect(Point2D(0, 0), Point2D(2, 2), Point2D(0, 2), Point2D(2, 0)) is True
    assert do_intersect(Point2D(0, 0), Point2D(1, 0), Point2D(2, 0), Point2D(3, 0)) is False

    diameter, far_pair = farthest_pair(points[:4])
    assert math.isclose(diameter, math.sqrt(8), abs_tol=1e-9)
    assert set(far_pair) in ({Point2D(0, 0), Point2D(2, 2)}, {Point2D(0, 2), Point2D(2, 0)})

    center, radius = welzl([Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)], [])
    assert center == Point2D(1, 1)
    assert math.isclose(radius, math.sqrt(2), abs_tol=1e-9)

    lec_center, lec_radius = LargestEmptyCircle.find([Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)])
    assert lec_center is not None
    assert lec_radius > 0

    sum_polygon = minkowski_sum(
        [Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(0, 1)],
        [Point2D(0, 0), Point2D(1, 0), Point2D(1, 2), Point2D(0, 2)],
    )
    coords = {(round(point.x, 6), round(point.y, 6)) for point in sum_polygon}
    assert coords == {(0, 0), (3, 0), (3, 3), (0, 3)}


def test_polygon_smoothing_and_distance_map_helpers():
    square = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]

    resampled = PolygonalMeanCurvatureFlow.resample_polygon(square, 8)
    assert len(resampled) == 8
    assert resampled[0] == Point2D(0, 0, 0)
    assert resampled[2] == Point2D(2, 0, 2)

    smoothed = PolygonalMeanCurvatureFlow.smooth(square, iterations=5, time_step=0.1)
    assert len(smoothed) == 4
    cx = sum(point.x for point in smoothed) / len(smoothed)
    cy = sum(point.y for point in smoothed) / len(smoothed)
    assert math.isclose(cx, 0.0, abs_tol=1e-9)
    assert math.isclose(cy, 0.0, abs_tol=1e-9)

    unchanged = PolygonalMeanCurvatureFlow.smooth(square[:2], iterations=3)
    assert unchanged == square[:2]

    empty_grid, empty_extent = DistanceMapSolver.solve([])
    assert empty_grid == [[]]
    assert empty_extent == (0, 0, 0, 0)

    grid, extent = DistanceMapSolver.solve(square, resolution=10, padding=0.0)
    assert len(grid) >= 3
    assert len(grid[0]) >= 3
    assert extent == (0.0, 2.0, 0.0, 2.0)
    assert grid[0][0] == 0.0

    svg = DistanceMapSolver.visualize_svg(grid, extent)
    assert svg.startswith('<svg width="')
    assert "<rect " in svg


def test_mesh_transfer_maps_boundary_to_target_polygon():
    vertices = [
        Point2D(0, 0),
        Point2D(1, 0),
        Point2D(1, 1),
        Point2D(0, 1),
        Point2D(0.5, 0.5),
    ]
    mesh = TriangleMesh(vertices, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
    target = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(0, 1)]

    transferred = MeshTransfer.transfer(mesh, target)

    assert transferred.faces == mesh.faces
    assert transferred.vertices[0] == Point2D(0, 0)
    assert transferred.vertices[1] == Point2D(1.5, 0)
    assert transferred.vertices[2] == Point2D(2, 1)
    assert transferred.vertices[3] == Point2D(0.5, 1)
    assert 0.0 <= transferred.vertices[4].x <= 2.0
    assert 0.0 <= transferred.vertices[4].y <= 1.0


def test_random_walkers_and_grid_paths_cover_core_helpers():
    random.seed(11)

    walk2d = RandomWalker.simulate_2d(3, 3, 1, 1, max_steps=5)
    walk3d = RandomWalker.simulate_3d(2, 2, 2, 0, 0, 0, max_steps=4)
    saw = RandomWalker.simulate_saw_2d(1, 3, 0, 1)

    assert walk2d["steps"] == 5
    assert walk2d["final_pos"] in walk2d["frequencies"]
    assert walk2d["unique_cells"] <= 6

    assert walk3d["steps"] == 4
    assert walk3d["final_pos"] in walk3d["frequencies"]
    assert walk3d["unique_cells"] <= 5

    assert saw["reason"] == "Trapped"
    assert saw["steps"] == 1
    assert saw["path"][0] == (0, 1)

    assert simulate_random_walk_2d(2, 2, 0, 0, 0)["steps"] == 0
    assert simulate_random_walk_3d(1, 1, 1, 0, 0, 0, 3)["steps"] == 0
    assert simulate_saw_2d(1, 1, 0, 0)["reason"] == "Success"

    zigzag = generate_zigzag_path(3, 2)
    spiral = generate_spiral_path(3, 3, 1, 1)
    assert len(zigzag) == 6
    assert len(set(zigzag)) == 6
    assert spiral[0] == (1, 1)
    assert len(set(spiral)) == 9


def test_space_filling_curve_generators_and_visualization():
    peano = SpaceFillingCurves.peano(1)
    hilbert = SpaceFillingCurves.hilbert(2)
    morton = SpaceFillingCurves.morton(2)
    zigzag = SpaceFillingCurves.zigzag(3, 2)
    sweep = SpaceFillingCurves.sweep(3, 2)
    svg = SpaceFillingCurves.visualize(sweep, 3, 2, cell_size=10)

    assert peano == [0, 1, 2, 5, 4, 3, 6, 7, 8]
    assert len(hilbert) == 16
    assert len(set(hilbert)) == 16
    assert len(morton) == 16
    assert len(set(morton)) == 16
    assert zigzag == [0, 1, 3, 4, 2, 5]
    assert sweep == [0, 1, 2, 5, 4, 3]
    assert svg.startswith('<svg width="')


def test_mesh_refinement_and_triangle_to_quad_conversion():
    mesh = TriangleMesh(
        [Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)],
        [(0, 1, 2)],
    )

    area = TriMeshRefiner._calculate_face_area(mesh.vertices[0], mesh.vertices[1], mesh.vertices[2])
    linear = TriMeshRefiner.subdivide_linear(mesh)
    refined = TriMeshRefiner.refine_uniform(mesh, max_area_ratio=0.2)
    quad_mesh = TriangleToQuadConverter.convert(mesh)

    assert math.isclose(area, 2.0, abs_tol=1e-9)
    assert len(linear.vertices) == 6
    assert len(linear.faces) == 4
    assert len(refined.vertices) > len(mesh.vertices)
    assert len(refined.faces) > len(mesh.faces)
    refined_threshold = area * 0.2
    for face in refined.faces:
        face_area = TriMeshRefiner._calculate_face_area(
            refined.vertices[face[0]],
            refined.vertices[face[1]],
            refined.vertices[face[2]],
        )
        assert face_area <= refined_threshold + 1e-9
    assert len(quad_mesh.vertices) == 7
    assert len(quad_mesh.faces) == 3

    centroid = quad_mesh.vertices[-1]
    assert centroid == Point2D(2.0 / 3.0, 2.0 / 3.0, 6)


def test_mesh_io_handlers_round_trip_common_formats():
    vertices2d = [Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2)]
    vertices3d = [Point3D(0, 0, 0, 0), Point3D(1, 0, 0, 1), Point3D(0, 1, 0, 2)]
    faces = [(0, 1, 2)]

    with tempfile.TemporaryDirectory(dir="/tmp") as tmp_dir:
        tmp = Path(tmp_dir)

        obj_path = tmp / "mesh.obj"
        off_path = tmp / "mesh.off"
        stl_ascii_path = tmp / "mesh_ascii.stl"
        stl_bin_path = tmp / "mesh_bin.stl"

        OBJFileHandler.write(str(obj_path), vertices2d, faces)
        obj_vertices, obj_faces = OBJFileHandler.read(str(obj_path))
        assert len(obj_vertices) == 3
        assert obj_faces == [[0, 1, 2]]
        assert OBJFileHandler.triangulate_faces([[0, 1, 2, 3]]) == [(0, 1, 2), (0, 2, 3)]

        OFFFileHandler.write(str(off_path), vertices3d, faces)
        off_vertices, off_faces = OFFFileHandler.read(str(off_path))
        assert len(off_vertices) == 3
        assert off_faces == [[0, 1, 2]]

        STLFileHandler.write(str(stl_ascii_path), vertices3d, faces, binary=False)
        assert STLFileHandler._is_binary(str(stl_ascii_path)) is False
        stl_ascii_vertices, stl_ascii_faces = STLFileHandler.read(str(stl_ascii_path))
        assert len(stl_ascii_vertices) == 3
        assert stl_ascii_faces == [[0, 1, 2]]

        STLFileHandler.write(str(stl_bin_path), vertices3d, faces, binary=True)
        assert STLFileHandler._is_binary(str(stl_bin_path)) is True
        stl_bin_vertices, stl_bin_faces = STLFileHandler.read(str(stl_bin_path))
        assert len(stl_bin_vertices) == 3
        assert stl_bin_faces == [[0, 1, 2]]

        mesh_vertices, mesh_faces = MeshImporter.read(str(obj_path))
        assert len(mesh_vertices) == 3
        assert mesh_faces == [[0, 1, 2]]

        written_obj = tmp / "mesh_out.obj"
        MeshExporter.write(str(written_obj), vertices3d, faces)
        assert written_obj.exists()


def test_geoplot_renders_mesh_polygon_voronoi_and_points():
    mesh = TriangleMesh([Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)], [(0, 1, 2)])
    polygon = Polygon([Point2D(0, 0), Point2D(2, 0), Point2D(1, 1)])
    diagram = VoronoiDiagram()
    diagram.compute([Point2D(0, 0, 0), Point2D(2, 0, 1)], boundary_type="square")
    points = [Point2D(0, 0), Point2D(1, 1)]

    svg = GeomPlot.get_image([mesh, polygon, diagram, points], format="svg", width=200, height=200)
    png = GeomPlot.get_image([mesh, points], format="png", width=64, height=64)

    assert svg.startswith('<svg viewBox="0 0 200 200"')
    assert "<polygon" in svg
    assert "<circle" in svg
    assert png.startswith(b"\x89PNG\r\n\x1a\n")

    normalized = GeomPlot._normalize_objects(points)
    assert normalized == [points]
    bounds = GeomPlot._get_bounds([mesh, polygon])
    assert bounds == (0, 0, 2, 1)


def test_shape_objects_expose_expected_geometry():
    seg2d = LineSegment(Point2D(0, 0), Point2D(3, 4))
    seg3d = LineSegment(Point3D(0, 0, 0), Point3D(1, 2, 2))
    ray = Ray(Point2D(1, 1), Point2D(2, 3))
    circle = Circle(Point2D(0, 0), 2)
    rect = Rectangle(Point2D(1, 1), 4, 2)
    square = Square(Point2D(0, 0), 3)
    tri = Triangle(Point2D(0, 0), Point2D(4, 0), Point2D(0, 3))
    plane = Plane(Point3D(0, 0, 0), (0, 0, 1))
    tetra = Tetrahedron(Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1))
    sphere = Sphere(Point3D(0, 0, 0), 2)
    cuboid = Cuboid(Point3D(0, 0, 0), 2, 3, 4)
    hexa = Hexahedron(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(1, 1, 0),
            Point3D(0, 1, 0),
            Point3D(0, 0, 1),
            Point3D(1, 0, 1),
            Point3D(1, 1, 1),
            Point3D(0, 1, 1),
        ]
    )

    assert math.isclose(seg2d.length, 5.0, abs_tol=1e-9)
    assert math.isclose(seg3d.length, 3.0, abs_tol=1e-9)
    assert ray.centroid == Point2D(1, 1)
    assert ray.diameter == float("inf")
    assert math.isclose(circle.area, 4 * math.pi, abs_tol=1e-9)
    assert math.isclose(circle.perimeter, 4 * math.pi, abs_tol=1e-9)
    assert rect.vertices == [Point2D(-1, 0), Point2D(3, 0), Point2D(3, 2), Point2D(-1, 2)]
    assert square.side_length == 3
    assert math.isclose(tri.area, 6.0, abs_tol=1e-9)
    assert math.isclose(tri.perimeter, 12.0, abs_tol=1e-9)
    assert plane.centroid == Point3D(0, 0, 0)
    assert math.isclose(tetra.volume, 1.0 / 6.0, abs_tol=1e-9)
    assert math.isclose(sphere.surface_area, 16 * math.pi, abs_tol=1e-9)
    assert cuboid.volume == 24
    assert cuboid.surface_area == 52
    assert math.isclose(hexa.volume, 1.0, abs_tol=1e-9)
    assert math.isclose(hexa.surface_area, 6.0, abs_tol=1e-9)


def test_circle_packer_handles_empty_and_packs_rectangle_domain():
    polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]

    assert CirclePacker.pack([], 1.0) == []
    assert CirclePacker.pack(polygon, 0.0) == []
    assert CirclePacker.optimal_radius([], 3) == 0.0

    centers = CirclePacker.pack(polygon, 0.5)
    efficiency = CirclePacker.calculate_efficiency(polygon, centers, 0.5)
    svg = CirclePacker.visualize(polygon, centers, 0.5, width=200, height=200)

    assert centers
    assert all(CirclePacker._is_circle_inside(center, 0.5, polygon) for center in centers)
    assert efficiency > 0
    assert svg.startswith('<svg width="200" height="200"')


def test_mesh_core_helpers_cover_topology_and_even_element_repairs():
    triangle_mesh = TriangleMesh(
        [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)],
        [(0, 1, 2), (0, 2, 3)],
    )
    quad_mesh = QuadMesh(
        [Point2D(0, 0), Point2D(1, 0), Point2D(2, 0), Point2D(2, 1), Point2D(1, 1), Point2D(0, 1)],
        [(0, 1, 4, 5), (1, 2, 3, 4)],
    )
    polygon_mesh = PolygonMesh(
        [Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(1, 2), Point2D(0, 1)],
        [(0, 1, 2, 3, 4)],
    )

    assert triangle_mesh.euler_characteristic() == 1
    assert triangle_mesh.centroid == Point2D(0.5, 0.5)
    assert triangle_mesh.bounding_box() == ((0, 0), (1, 1))
    assert triangle_mesh.topology.boundary_edges() == [(0, 1), (1, 2), (2, 3), (0, 3)]
    assert triangle_mesh.topology.vertex_neighbors(0) == {1, 2, 3}
    assert triangle_mesh.topology.element_neighbors(0) == {1}
    assert triangle_mesh.topology.shared_edge_neighbors(0) == {1}

    split_even = TriangleMesh([Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)], [(0, 1, 2)]).ensure_even_elements()
    assert len(split_even.faces) % 2 == 0
    assert len(split_even.vertices) > 3

    odd_two = TriangleMesh(
        [Point2D(0, 0), Point2D(2, 0), Point2D(1, 1), Point2D(0, 2), Point2D(2, 2)],
        [(0, 1, 2), (0, 2, 3), (1, 4, 2)],
    )
    even_two = odd_two.ensure_even_elements()
    assert len(even_two.faces) % 2 == 0

    chord = quad_mesh.extract_chord(0, 1)
    assert chord == [0, 1]

    triangulated = polygon_mesh.triangulate()
    assert len(triangulated.faces) == 3
    assert polygon_mesh.euler_characteristic() == 1

    triangle_mesh.reorder_nodes([2, 1, 0, 3])
    assert triangle_mesh.vertices[0] == Point2D(1, 1)
    assert set(triangle_mesh.elements) == {(2, 1, 0), (2, 0, 3)}


def test_mesh_and_triangle_utilities_cover_standalone_helpers():
    tris = [
        (Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2)),
        (Point2D(1, 0, 1), Point2D(1, 1, 3), Point2D(0, 1, 2)),
    ]

    assert len(build_topology(tris)) == 2
    assert is_delaunay(build_topology(tris)) is True
    assert get_nondelaunay_triangles(build_topology(tris)) == set()

    assert len(DelaunayMesher.build_mesh_topology(tris)) == 2
    mesh = DelaunayMesher._to_triangle_mesh(tris)
    assert isinstance(mesh, TriangleMesh)
    assert mesh.faces == [(0, 1, 2), (1, 3, 2)]

    tri_mesh = DelaunayMesher.triangulate(
        [Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2), Point2D(1, 1, 3)],
        algorithm="incremental",
    )
    assert isinstance(tri_mesh, TriangleMesh)
    constrained = DelaunayMesher.constrained_triangulate(
        [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
    )
    assert isinstance(constrained, TriangleMesh)
    dynamic = DelaunayMesher.dynamic_triangulate(10, 10)
    assert isinstance(dynamic, DynamicDelaunay)
    assert DelaunayMesher.check_is_delaunay(build_topology(tris)) is True
    assert DelaunayMesher.find_bad_triangles(build_topology(tris)) == set()

    with pytest.raises(ValueError):
        DelaunayMesher.triangulate([Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)], algorithm="unknown")

    mesh = triangulate([Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2), Point2D(0, 1, 2)])
    assert isinstance(mesh, TriangleMesh)


def test_dynamic_and_low_level_triangle_classes():
    outer = DTriangle(Point2D(0, 0, 0), Point2D(5, 0, 1), Point2D(0, 5, 2))
    neighbor = DTriangle(Point2D(5, 0, 1), Point2D(5, 5, 3), Point2D(0, 5, 2))
    outer.set_neighbor(0, neighbor)
    assert outer.n[0] is neighbor
    assert neighbor.contains_point(Point2D(3, 3)) is True
    assert neighbor.has_vertex(Point2D(5, 5, 3)) is True

    dyn = DynamicDelaunay(10, 10)
    p0 = Point2D(1, 1, 0)
    p1 = Point2D(3, 1, 1)
    p2 = Point2D(2, 3, 2)
    for point in [p0, p1, p2]:
        dyn.add_point(point)
    containing = dyn.find_containing_triangle(Point2D(2, 2))
    assert containing is not None
    assert dyn.get_triangles()

    tri = MeshTriangle(Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2))
    other = MeshTriangle(Point2D(1, 0, 1), Point2D(1, 1, 3), Point2D(0, 1, 2))
    tri.neighbors[0] = other
    assert tri.get_edge(0) == (1, 2)
    assert tri.find_neighbor_index(other) == 0


def test_point_tree_helpers_cover_quadtree_display_and_simplifier(capsys):
    quadtree = PointQuadtree()
    assert quadtree.insert(Point2D(0, 0, 0)) is True
    assert quadtree.insert(Point2D(1, 1, 1)) is True
    assert quadtree.insert(Point2D(-1, 1, 2)) is True
    assert quadtree.insert(Point2D(1, -1, 3)) is True
    assert quadtree.insert(Point2D(-1, -1, 4)) is True
    assert quadtree.insert(Point2D(0, 0, 9)) is False
    assert quadtree.count == 5
    assert PointQuadtree._get_quadrant_name(Point2D(0, 0), Point2D(1, -1)) == "se"
    quadtree.display()
    captured = capsys.readouterr().out
    assert "Root: P0(0, 0)" in captured
    assert "NE:" in captured and "NW:" in captured and "SE:" in captured and "SW:" in captured

    kd = build_kdtree([Point2D(0, 0), Point2D(1, 1), Point2D(2, 2)])
    display_kdtree(kd)
    captured = capsys.readouterr().out
    assert "[Depth 0, Split X]" in captured

    bbox2d, is_3d = PointSimplifier.get_bounding_box([Point2D(0, 0), Point2D(2, 3)])
    assert bbox2d == (0, 2, 0, 3)
    assert is_3d is False

    bbox3d, is_3d = PointSimplifier.get_bounding_box([Point3D(0, 0, 0), Point3D(2, 3, 4)])
    assert bbox3d == (0, 2, 0, 3, 0, 4)
    assert is_3d is True

    points2d = [Point2D(0, 0, 0), Point2D(0.05, 0.05, 1), Point2D(1, 1, 2), Point2D(2, 2, 3)]
    simplified2d = PointSimplifier.simplify(points2d, ratio=0.5, protected_ids={1})
    assert Point2D(0.05, 0.05, 1) in simplified2d
    assert len(simplified2d) < len(points2d)
    assert PointSimplifier.simplify(points2d, ratio=0.0) == points2d
    assert PointSimplifier.simplify([], ratio=0.2) == []

    points3d = [Point3D(0, 0, 0, 0), Point3D(0.01, 0.01, 0.01, 1), Point3D(1, 1, 1, 2)]
    simplified3d = PointSimplifier.simplify(points3d, ratio=0.5)
    assert len(simplified3d) <= 2


def test_delaunay_remaining_paths_cover_divide_and_conquer_and_flips():
    points = [Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2), Point2D(1, 1, 3)]
    mesh_dc = DelaunayMesher.triangulate(points, algorithm="divide_and_conquer")
    assert isinstance(mesh_dc, TriangleMesh)

    mesh_flip = DelaunayMesher.triangulate(
        [Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2), Point2D(1, 1, 3)],
        algorithm="flip",
    )
    assert isinstance(mesh_flip, TriangleMesh)

    non_delaunay = build_topology(
        [
            (Point2D(0, 0, 0), Point2D(2, 0, 1), Point2D(0, 2, 2)),
            (Point2D(2, 0, 1), Point2D(0.5, 0.5, 3), Point2D(0, 2, 2)),
        ]
    )
    assert is_delaunay(non_delaunay) is False
    assert DelaunayMesher.find_bad_triangles(non_delaunay)
    DelaunayMesher.improve_by_flipping(non_delaunay)

def test_visualization_helpers_generate_and_save_outputs(monkeypatch):
    svg = generate_svg_path([0, 1, 3, 2], width=2, height=2, cell_size=10, stroke_color="blue", stroke_width=3)
    assert svg.startswith('<svg width="20" height="20"')
    assert 'stroke="blue"' in svg
    assert generate_svg_path([], 2, 2) == ""

    with tempfile.TemporaryDirectory(dir="/tmp") as tmp_dir:
        out = Path(tmp_dir) / "curve.svg"
        save_svg(svg, str(out))
        assert out.read_text().startswith('<svg width="20"')

    calls = []

    def fake_run(args, check, capture_output):
        calls.append(args)
        if args[0] == "rsvg-convert":
            raise FileNotFoundError
        return None

    monkeypatch.setattr("subprocess.run", fake_run)
    with tempfile.TemporaryDirectory(dir="/tmp") as tmp_dir:
        out = Path(tmp_dir) / "curve.png"
        save_png(svg, str(out))
    assert calls[0][0] == "rsvg-convert"
    assert calls[1][0] == "convert"

    def failing_run(args, check, capture_output):
        raise FileNotFoundError

    monkeypatch.setattr("subprocess.run", failing_run)
    with tempfile.TemporaryDirectory(dir="/tmp") as tmp_dir:
        with pytest.raises(RuntimeError):
            save_png(svg, str(Path(tmp_dir) / "curve.png"))


def test_mesh_voxelizer_native_and_fallback_paths(monkeypatch):
    mesh = TriangleMesh(
        [
            Point3D(0, 0, 0, 0),
            Point3D(1, 0, 0, 1),
            Point3D(0, 1, 1, 2),
        ],
        [(0, 1, 2)],
    )

    voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=False)
    assert voxels
    assert all(len(v) == 3 for v in voxels)

    filled_voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=True)
    assert filled_voxels.issuperset(voxels)

    called = {"native": False}

    def fake_openvdb(*args, **kwargs):
        raise ImportError

    def fake_native(m, voxel_size, fill_interior=False):
        called["native"] = True
        return {(0, 0, 0)}

    monkeypatch.setattr(MeshVoxelizer, "voxelize_openvdb", staticmethod(fake_openvdb))
    monkeypatch.setattr(MeshVoxelizer, "voxelize_native", staticmethod(fake_native))
    result = MeshVoxelizer.voxelize(mesh, voxel_size=1.0, fill_interior=True)
    assert called["native"] is True
    assert result == {(0, 0, 0)}

    with pytest.raises(ImportError):
        MeshVoxelizer.save_vdb(object(), "/tmp/unused.vdb")


def test_cli_shared_helpers_and_polygon_generator(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", StringIO("1 2\n\n3 4\n"))
    assert cli_shared.read_stdin_lines() == ["1 2\n", "\n", "3 4\n"]

    monkeypatch.setattr("sys.stdin", StringIO("1 2\n\n3 4\n"))
    assert cli_shared.read_nonempty_stdin_lines() == ["1 2", "3 4"]

    cli_shared.print_lines(["alpha", "beta"])
    assert capsys.readouterr().out == "alpha\nbeta\n"

    assert cli_shared.parse_points(["1 2", "bad", "3 4"]) == [Point2D(1, 2, 0), Point2D(3, 4, 1)]
    assert cli_shared.parse_points(["7 1 2", "8 3 4"], with_ids=True) == [Point2D(1, 2, 7), Point2D(3, 4, 8)]
    assert cli_shared.parse_point_line("1 2", point_id=5) == Point2D(1, 2, 5)
    assert cli_shared.parse_point_fields(["9", "1", "2"], with_id=True) == Point2D(1, 2, 9)
    assert cli_shared.parse_point_fields(["x", "y"]) is None
    assert cli_shared.format_point(Point2D(1, 2)) == "(1.000000, 2.000000)"
    assert len(cli_shared.demo_points()) == 6
    assert len(cli_shared.demo_polygon()) == 6
    assert cli_shared.demo_mesh_lines()[-1] == "1 3 2\n"

    random.seed(5)
    convex = PolygonGenerator.convex(8, (0, 10), (0, 10))
    concave = PolygonGenerator.concave(8, (0, 10), (0, 10))
    star = PolygonGenerator.star_shaped(8, center=Point2D(0, 0), max_radius=10)
    assert len(convex) >= 3
    assert len(concave) == 8
    assert len(star) == 8


def test_polygon_boolean_helper_functions_cover_remaining_branches():
    square = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
    shifted = [Point2D(3, 0), Point2D(5, 0), Point2D(5, 2), Point2D(3, 2)]
    nested = [Point2D(0.5, 0.5), Point2D(1.5, 0.5), Point2D(1.5, 1.5), Point2D(0.5, 1.5)]

    assert math.isclose(centroid(square).x, 1.0, abs_tol=1e-9)
    assert representative_point(square) == Point2D(1, 1)
    assert polygon_edges(square)[0] == (Point2D(0, 0), Point2D(2, 0))
    assert boolean_point_key(Point2D(1, 2)) == (1000000000, 2000000000)
    assert point_on_segment(Point2D(1, 0), Point2D(0, 0), Point2D(2, 0)) is True
    assert set(segment_intersection_points((Point2D(0, 0), Point2D(2, 0)), (Point2D(1, 0), Point2D(3, 0)))) == {Point2D(1, 0), Point2D(2, 0)}

    split, intersections = split_polygon_edges_against_other(
        polygon_edges(square),
        polygon_edges([Point2D(1, -1), Point2D(1, 3), Point2D(3, 3), Point2D(3, -1)]),
    )
    assert split
    assert intersections

    assert handle_no_intersection_case("union", square, shifted) == [{"outer": square, "holes": []}, {"outer": shifted, "holes": []}]
    assert handle_no_intersection_case("difference", square, nested) == [{"outer": square, "holes": [list(reversed(nested))]}]

    directed, special = build_boundary_segments(square, shifted, "union")
    assert special is not None or directed is not None

    loops = trace_directed_loops(
        [
            (Point2D(0, 0), Point2D(1, 0)),
            (Point2D(1, 0), Point2D(1, 1)),
            (Point2D(1, 1), Point2D(0, 1)),
            (Point2D(0, 1), Point2D(0, 0)),
        ]
    )
    assert len(loops) == 1
    deduped = deduplicate_polygons([square, list(reversed(square))])
    assert len(deduped) == 1
    assert polygon_key(deduped[0]) == polygon_key(square)
    assert polygon_key(square) == polygon_key(list(reversed(square)))
    assert parse_polygon(["", "4", "0 0", "2 0", "2 2", "0 2"], 0)[0] == square
    assert boolean_format_point(Point2D(1, 2)) == "(1.000000, 2.000000)"


def test_reflection_polygon_helpers_and_viewer(monkeypatch, capsys):
    square = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]

    assert reflection_cli._normalize(Point2D(3, 4)) == Point2D(0.6, 0.8)
    with pytest.raises(ValueError):
        reflection_cli._normalize(Point2D(0, 0))

    assert reflection_cli._signed_area_twice(list(reversed(square))) < 0
    assert reflection_cli._ensure_ccw(list(reversed(square))) == square
    assert reflection_cli._parse_point("1 2", "origin") == Point2D(1, 2)
    with pytest.raises(ValueError):
        reflection_cli._parse_point("1 2 3", "origin")

    origin, direction, polygon = reflection_cli.parse_input(["1 1", "2 0", "0 0", "4 0", "4 4", "0 4"])
    assert origin == Point2D(1, 1)
    assert direction == Point2D(1, 0)
    assert polygon == square

    with pytest.raises(ValueError):
        reflection_cli.parse_input(["1 1", "1 0", "0 0", "1 1"])
    with pytest.raises(ValueError):
        reflection_cli.parse_input(["5 5", "1 0", "0 0", "4 0", "4 4", "0 4"])

    assert reflection_cli._ray_segment_intersection(Point2D(1, 1), Point2D(1, 0), Point2D(4, 0), Point2D(4, 4)) == (3.0, 0.25)
    assert reflection_cli._ray_segment_intersection(Point2D(1, 1), Point2D(0, 1), Point2D(0, 0), Point2D(4, 0)) is None

    reflected = reflection_cli._reflect(Point2D(1, -1), Point2D(0, 0), Point2D(4, 0))
    assert reflected == Point2D(1 / math.sqrt(2), 1 / math.sqrt(2))
    with pytest.raises(ValueError):
        reflection_cli._reflect(Point2D(1, 0), Point2D(0, 0), Point2D(0, 0))

    hit, next_state = reflection_cli.advance_ray(reflection_cli.RayState(Point2D(1, 1), Point2D(1, 0)), square)
    assert hit == Point2D(4, 1)
    assert next_state.direction == Point2D(-1, 0)

    path = reflection_cli.simulate_reflections(Point2D(1, 1), Point2D(1, 0), square, steps=3)
    assert path == [Point2D(1, 1), Point2D(4, 1), Point2D(0, 1), Point2D(4, 1)]

    with pytest.raises(ValueError):
        reflection_cli.advance_ray(reflection_cli.RayState(Point2D(0, 0), Point2D(1, 0)), [Point2D(0, 0), Point2D(1, 0)])

    class FakeCanvas:
        def __init__(self, root, width, height, bg, highlightthickness):
            self.lines = []
            self.polygons = []
            self.ovals = []

        def pack(self, **kwargs):
            return None

        def create_polygon(self, coords, outline, fill, width):
            self.polygons.append((coords, outline, fill, width))

        def create_oval(self, *args, **kwargs):
            self.ovals.append((args, kwargs))

        def create_line(self, *args, **kwargs):
            self.lines.append((args, kwargs))

    class FakeRoot:
        def __init__(self):
            self.after_calls = []
            self.title_text = None

        def title(self, text):
            self.title_text = text

        def after(self, delay, callback):
            self.after_calls.append(delay)

        def mainloop(self):
            self.mainloop_called = True

    class FakeTkModule:
        BOTH = "both"

        def __init__(self):
            self.root = FakeRoot()

        def Tk(self):
            return self.root

        Canvas = FakeCanvas

    import sys

    fake_tk = FakeTkModule()
    monkeypatch.setitem(sys.modules, "tkinter", fake_tk)
    viewer = reflection_cli.ReflectionViewer(square, Point2D(1, 1), Point2D(1, 0))
    assert viewer.root.title_text == "Ray Reflection in a Polygon"
    assert viewer.canvas.polygons
    assert viewer.canvas.ovals
    assert viewer.canvas.lines
    assert viewer.root.after_calls == [reflection_cli.ANIMATION_DELAY_MS]
    viewer.run()
    assert viewer.root.mainloop_called is True

    monkeypatch.setattr(reflection_cli, "ReflectionViewer", lambda polygon, origin, direction: type("Viewer", (), {"run": lambda self: print("ran")})())
    assert reflection_cli.main() == 0
    assert capsys.readouterr().out == "ran\n"

    class MissingTkViewer:
        def __init__(self, polygon, origin, direction):
            raise ModuleNotFoundError("tkinter")

    monkeypatch.setattr(reflection_cli, "ReflectionViewer", MissingTkViewer)
    assert reflection_cli.main() == 1
    captured = capsys.readouterr().out
    assert "Unable to start viewer" in captured
    assert "tkinter support" in captured


def test_voronoi_square_compute_and_triangle_to_quad_edge_reuse():
    diagram = VoronoiDiagram()
    points = [Point2D(0, 0, 0), Point2D(2, 0, 1), Point2D(1, 2, 2)]
    mesh = diagram.compute(points)

    assert len(diagram.boundary) == 4
    assert len(diagram.cells) == 3
    assert len(mesh.vertices) >= 3
    assert len(mesh.elements) == 3
    for _, cell in diagram.cells:
        assert cell
        for vertex in cell:
            assert -1.0 <= vertex.x <= 3.0
            assert -0.5 <= vertex.y <= 2.5

    mesh2d = TriangleMesh(
        [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)],
        [(0, 1, 2), (0, 2, 3)],
    )
    quads2d = TriangleToQuadConverter.convert(mesh2d)
    assert len(quads2d.faces) == 6
    assert len(quads2d.vertices) == 11
    shared_midpoints = [
        index
        for index, vertex in enumerate(quads2d.vertices)
        if isinstance(vertex, Point2D) and vertex == Point2D(0.5, 0.5, index)
    ]
    assert shared_midpoints == [6]

    mesh3d = TriangleMesh(
        [Point3D(0, 0, 0, 0), Point3D(2, 0, 0, 1), Point3D(0, 2, 2, 2)],
        [(0, 1, 2)],
    )
    quads3d = TriangleToQuadConverter.convert(mesh3d)
    assert isinstance(quads3d.vertices[3], Point3D)
    assert quads3d.vertices[-1] == Point3D(2 / 3, 2 / 3, 2 / 3, 6)


def test_line_arrangement_cli_helpers_and_main(capsys):
    assert line_cli.point_key(Point2D(0.0, 0.0)) == (0, 0)
    assert line_cli.polygon_key([Point2D(1, 0), Point2D(1, 1), Point2D(0, 1), Point2D(0, 0)]) == line_cli.polygon_key(
        [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    )
    assert math.isclose(line_cli.segment_parameter(Point2D(2, 0), Point2D(0, 0), Point2D(4, 0)), 0.5, abs_tol=1e-9)
    assert math.isclose(line_cli.segment_parameter(Point2D(0, 3), Point2D(0, 0), Point2D(0, 6)), 0.5, abs_tol=1e-9)
    assert math.isclose(line_cli.signed_polygon_area([Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)]), 2.0, abs_tol=1e-9)
    assert line_cli.canonical_segment((Point2D(1, 1), Point2D(0, 0))) == (Point2D(0, 0), Point2D(1, 1))

    crossing = line_cli.segment_intersection_points((Point2D(0, 0), Point2D(2, 2)), (Point2D(0, 2), Point2D(2, 0)))
    overlap = line_cli.segment_intersection_points((Point2D(0, 0), Point2D(3, 0)), (Point2D(1, 0), Point2D(2, 0)))
    separate = line_cli.segment_intersection_points((Point2D(0, 0), Point2D(1, 0)), (Point2D(0, 1), Point2D(1, 1)))
    assert crossing == [Point2D(1, 1)]
    assert set(overlap) == {Point2D(1, 0), Point2D(2, 0)}
    assert separate == []

    segments = [
        (Point2D(0, 0), Point2D(2, 2)),
        (Point2D(0, 2), Point2D(2, 0)),
        (Point2D(0, 1), Point2D(2, 1)),
    ]
    intersections = line_cli.find_intersection_points(segments)
    split = line_cli.split_segments(segments)
    vertices, neighbors = line_cli.build_graph(split)
    faces = line_cli.trace_faces(vertices, neighbors)
    arrangement = line_cli.analyze_arrangement(segments)

    assert Point2D(1, 1) in intersections
    assert len(split) > len(segments)
    assert vertices
    assert all(neighbors.values())
    assert faces == []
    assert arrangement[0]
    assert arrangement[1]
    assert arrangement[2] == []

    square_segments = [
        (Point2D(0, 0), Point2D(1, 0)),
        (Point2D(1, 0), Point2D(1, 1)),
        (Point2D(1, 1), Point2D(0, 1)),
        (Point2D(0, 1), Point2D(0, 0)),
    ]
    _, split_square, polygons = line_cli.analyze_arrangement(square_segments)
    assert len(split_square) == 4
    assert len(polygons) == 1

    parsed = line_cli.parse_segments(["0 0 1 0", "", "1 0 1 1", "2 2 2 2"])
    assert parsed == [(Point2D(0, 0), Point2D(1, 0)), (Point2D(1, 0), Point2D(1, 1))]
    with pytest.raises(ValueError):
        line_cli.parse_segments(["0 0 1"])

    assert line_cli.format_point(Point2D(1, 2)) == "(1.000000, 2.000000)"
    assert line_cli.main() == 0
    out = capsys.readouterr().out
    assert "Intersection Points:" in out
    assert "Non-Intersecting Segments:" in out
    assert "Polygons:" in out


def test_shape_objects_cover_remaining_properties_and_repr():
    seg2d = LineSegment(Point2D(0, 0), Point2D(2, 2))
    seg3d = LineSegment(Point3D(0, 0, 0), Point3D(2, 2, 2))
    ray = Ray(Point3D(0, 0, 0), Point3D(1, 1, 1))
    circle = Circle(Point2D(1, 2), 3)
    rect = Rectangle(Point2D(0, 0), 6, 8)
    square = Square(Point2D(1, 1), 2)
    tri = Triangle(Point2D(0, 0), Point2D(3, 0), Point2D(0, 4))
    plane = Plane(Point3D(1, 2, 3), (0, 1, 0))
    tetra = Tetrahedron(Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1))
    sphere = Sphere(Point3D(1, 1, 1), 3)
    cuboid = Cuboid(Point3D(0, 0, 0), 2, 4, 6)
    hexa = Hexahedron(
        [
            Point3D(0, 0, 0),
            Point3D(2, 0, 0),
            Point3D(2, 2, 0),
            Point3D(0, 2, 0),
            Point3D(0, 0, 2),
            Point3D(2, 0, 2),
            Point3D(2, 2, 2),
            Point3D(0, 2, 2),
        ]
    )

    assert seg2d.centroid == Point2D(1, 1)
    assert seg3d.centroid == Point3D(1, 1, 1)
    assert seg2d.diameter == seg2d.length
    assert ray.centroid == Point3D(0, 0, 0)
    assert ray.diameter == float("inf")
    assert circle.radius == 3
    assert circle.centroid == Point2D(1, 2)
    assert circle.diameter == 6
    assert rect.width == 6
    assert rect.height == 8
    assert math.isclose(rect.diameter, 10.0, abs_tol=1e-9)
    assert rect.area == 48
    assert rect.perimeter == 28
    assert square.centroid == Point2D(1, 1)
    assert square.side_length == 2
    assert tri.centroid == Point2D(1, 4 / 3)
    assert math.isclose(tri.diameter, 5.0, abs_tol=1e-9)
    assert plane.centroid == Point3D(1, 2, 3)
    assert plane.diameter == float("inf")
    assert tetra.centroid == Point3D(0.25, 0.25, 0.25)
    assert tetra.diameter > 1.0
    assert tetra.surface_area > 2.0
    assert sphere.radius == 3
    assert sphere.centroid == Point3D(1, 1, 1)
    assert sphere.diameter == 6
    assert math.isclose(sphere.volume, 36 * math.pi, abs_tol=1e-9)
    assert cuboid.centroid == Point3D(0, 0, 0)
    assert math.isclose(cuboid.diameter, math.sqrt(56), abs_tol=1e-9)
    assert hexa.centroid == Point3D(1, 1, 1)
    assert math.isclose(hexa.diameter, math.sqrt(12), abs_tol=1e-9)
    assert math.isclose(hexa.volume, 8.0, abs_tol=1e-9)
    assert math.isclose(hexa.surface_area, 24.0, abs_tol=1e-9)
    with pytest.raises(ValueError):
        Hexahedron([Point3D(0, 0, 0)] * 7)

    assert "LineSegment" in repr(seg2d)
    assert "Ray(" in repr(ray)
    assert "Circle(" in repr(circle)
    assert "Rectangle(" in repr(rect)
    assert "Square(" in repr(square)
    assert "Triangle(" in repr(tri)
    assert "Plane(" in repr(plane)
    assert "Tetrahedron(" in repr(tetra)
    assert "Sphere(" in repr(sphere)
    assert "Cuboid(" in repr(cuboid)
    assert "Hexahedron(" in repr(hexa)


def test_circle_packer_covers_edge_cases_and_efficiency():
    square = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
    line_polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(8, 0)]

    assert CirclePacker.optimal_radius(square, 0) == 0.0
    assert CirclePacker.optimal_radius(line_polygon, 2) == 0.0
    assert CirclePacker._is_circle_inside(Point2D(5, 5), 0.5, square) is False
    assert CirclePacker._is_circle_inside(Point2D(0.25, 0.25), 0.5, square) is False
    assert CirclePacker.calculate_efficiency(line_polygon, [Point2D(1, 0)], 0.5) == 0.0

    radius = CirclePacker.optimal_radius(square, 4, tolerance=1e-3)
    centers = CirclePacker.pack(square, radius)
    svg = CirclePacker.visualize(square, centers, radius, width=100, height=80, padding=10)

    assert radius > 0
    assert len(centers) >= 4
    assert svg.startswith('<svg width="100" height="80"')
    assert svg.count("<circle") == len(centers)
