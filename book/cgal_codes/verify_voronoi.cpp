#include "point_io.h"

#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Object.h>

#include <algorithm>
#include <iostream>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: verify_voronoi points.{txt,obj,off}\n";
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
  std::size_t invalid_duals = 0;
  std::size_t segments = 0, rays = 0, lines = 0, duals = 0;
  bool triangulation_valid = false;

  if (!is_3d) {
    using Triangulation = CGAL::Delaunay_triangulation_2<Kernel>;
    Triangulation triangulation;
    for (const auto& row : rows) triangulation.insert(Kernel::Point_2(row[0], row[1]));
    triangulation_valid = triangulation.is_valid();
    for (auto edge = triangulation.finite_edges_begin();
         edge != triangulation.finite_edges_end(); ++edge) {
      const CGAL::Object dual = triangulation.dual(*edge);
      if (CGAL::object_cast<Kernel::Segment_2>(&dual)) ++segments;
      else if (CGAL::object_cast<Kernel::Ray_2>(&dual)) ++rays;
      else if (CGAL::object_cast<Kernel::Line_2>(&dual)) ++lines;
      else ++invalid_duals;
      ++duals;
    }
    std::cout << "dimension: 2\ninput sites: " << rows.size()
              << "\nfinite Delaunay edges: " << duals
              << "\nVoronoi segments: " << segments << "\nVoronoi rays: " << rays
              << "\nVoronoi lines: " << lines << '\n';
  } else {
    using Triangulation = CGAL::Delaunay_triangulation_3<Kernel>;
    Triangulation triangulation;
    for (const auto& row : rows)
      triangulation.insert(Kernel::Point_3(row[0], row[1], row[2]));
    triangulation_valid = triangulation.is_valid();
    for (auto facet = triangulation.finite_facets_begin();
         facet != triangulation.finite_facets_end(); ++facet) {
      const CGAL::Object dual = triangulation.dual(*facet);
      if (CGAL::object_cast<Kernel::Segment_3>(&dual)) ++segments;
      else if (CGAL::object_cast<Kernel::Ray_3>(&dual)) ++rays;
      else if (CGAL::object_cast<Kernel::Line_3>(&dual)) ++lines;
      else ++invalid_duals;
      ++duals;
    }
    std::cout << "dimension: 3\ninput sites: " << rows.size()
              << "\nfinite Delaunay facets: " << duals
              << "\nVoronoi segments: " << segments << "\nVoronoi rays: " << rays
              << "\nVoronoi lines: " << lines << '\n';
  }

  const bool valid = triangulation_valid && invalid_duals == 0;
  std::cout << "Delaunay triangulation valid: " << (triangulation_valid ? "true" : "false")
            << "\nall Voronoi duals valid: " << (invalid_duals == 0 ? "true" : "false")
            << "\nverification: " << (valid ? "PASS" : "FAIL") << '\n';
  return valid ? 0 : 1;
}
