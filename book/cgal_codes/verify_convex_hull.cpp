#include "point_io.h"

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Side_of_triangle_mesh.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/convex_hull_2.h>
#include <CGAL/convex_hull_3.h>

#include <algorithm>
#include <iostream>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: verify_convex_hull points.{txt,obj,off}\n";
    return 2;
  }
  std::vector<std::vector<double>> rows;
  try {
    rows = compgeom::read_rows_auto(argv[1]);
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
  if (rows.empty()) {
    std::cerr << "input file contains no points\n";
    return 1;
  }
  const bool is_3d = rows.front().size() == 3 &&
                    std::any_of(rows.begin(), rows.end(),
                                [](const auto& row) { return row[2] != 0.0; });
  std::size_t violations = 0;

  if (!is_3d) {
    std::vector<Kernel::Point_2> points;
    for (const auto& row : rows) points.emplace_back(row[0], row[1]);
    std::vector<Kernel::Point_2> hull;
    CGAL::convex_hull_2(points.begin(), points.end(), std::back_inserter(hull));
    const CGAL::Polygon_2<Kernel> polygon(hull.begin(), hull.end());
    for (const auto& point : points)
      if (polygon.bounded_side(point) == CGAL::ON_UNBOUNDED_SIDE) ++violations;
    std::cout << "dimension: 2\npoints: " << points.size()
              << "\nhull vertices: " << hull.size()
              << "\nconvex: " << (CGAL::is_convex_2(hull.begin(), hull.end()) ? "true" : "false")
              << "\nall points inside or on hull: " << (violations == 0 ? "true" : "false")
              << "\nviolations: " << violations << '\n';
  } else {
    std::vector<Kernel::Point_3> points;
    for (const auto& row : rows) points.emplace_back(row[0], row[1], row[2]);
    CGAL::Surface_mesh<Kernel::Point_3> hull;
    CGAL::convex_hull_3(points.begin(), points.end(), hull);
    CGAL::Side_of_triangle_mesh<CGAL::Surface_mesh<Kernel::Point_3>, Kernel> side(hull);
    for (const auto& point : points)
      if (side(point) == CGAL::ON_UNBOUNDED_SIDE) ++violations;
    std::cout << "dimension: 3\npoints: " << points.size()
              << "\nhull vertices: " << num_vertices(hull)
              << "\nhull faces: " << num_faces(hull)
              << "\nall points inside or on hull: " << (violations == 0 ? "true" : "false")
              << "\nviolations: " << violations << '\n';
  }
  return violations == 0 ? 0 : 1;
}
