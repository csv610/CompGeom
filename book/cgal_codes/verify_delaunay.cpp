#include "point_io.h"

#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

#include <algorithm>
#include <iostream>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: verify_delaunay points.{txt,obj,off}\n";
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
  bool valid = false;

  if (!is_3d) {
    using Triangulation = CGAL::Delaunay_triangulation_2<Kernel>;
    Triangulation triangulation;
    for (const auto& row : rows) triangulation.insert(Kernel::Point_2(row[0], row[1]));
    valid = triangulation.is_valid(true);
    std::cout << "dimension: 2\ninput sites: " << rows.size()
              << "\nvertices: " << triangulation.number_of_vertices()
              << "\nfinite faces: " << triangulation.number_of_faces()
              << "\nDelaunay mesh valid: " << (valid ? "true" : "false") << '\n';
  } else {
    using Triangulation = CGAL::Delaunay_triangulation_3<Kernel>;
    Triangulation triangulation;
    for (const auto& row : rows)
      triangulation.insert(Kernel::Point_3(row[0], row[1], row[2]));
    valid = triangulation.is_valid(true);
    std::cout << "dimension: 3\ninput sites: " << rows.size()
              << "\nvertices: " << triangulation.number_of_vertices()
              << "\nfinite cells: " << triangulation.number_of_finite_cells()
              << "\nDelaunay mesh valid: " << (valid ? "true" : "false") << '\n';
  }
  std::cout << "verification: " << (valid ? "PASS" : "FAIL") << '\n';
  return valid ? 0 : 1;
}
