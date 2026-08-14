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
    std::cerr << "usage: voronoi points.{txt,obj,off}\n";
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
  if (!is_3d) {
    using Triangulation = CGAL::Delaunay_triangulation_2<Kernel>;
    Triangulation triangulation;
    for (const auto& row : rows) triangulation.insert(Kernel::Point_2(row[0], row[1]));
    std::size_t finite_edges = 0, segments = 0, rays = 0, lines = 0;
    for (auto edge = triangulation.finite_edges_begin();
         edge != triangulation.finite_edges_end(); ++edge) {
      ++finite_edges;
      const CGAL::Object dual = triangulation.dual(*edge);
      if (CGAL::object_cast<Kernel::Segment_2>(&dual)) ++segments;
      else if (CGAL::object_cast<Kernel::Ray_2>(&dual)) ++rays;
      else if (CGAL::object_cast<Kernel::Line_2>(&dual)) ++lines;
    }
    std::cout << "dimension: 2\n sites: " << rows.size()
              << "\nfinite Delaunay edges: " << finite_edges
              << "\nVoronoi segments: " << segments << "\nVoronoi rays: " << rays
              << "\nVoronoi lines: " << lines << '\n';
  } else {
    using Triangulation = CGAL::Delaunay_triangulation_3<Kernel>;
    Triangulation triangulation;
    for (const auto& row : rows)
      triangulation.insert(Kernel::Point_3(row[0], row[1], row[2]));
    std::size_t finite_facets = 0, segments = 0, rays = 0, lines = 0;
    for (auto facet = triangulation.finite_facets_begin();
         facet != triangulation.finite_facets_end(); ++facet) {
      ++finite_facets;
      const CGAL::Object dual = triangulation.dual(*facet);
      if (CGAL::object_cast<Kernel::Segment_3>(&dual)) ++segments;
      else if (CGAL::object_cast<Kernel::Ray_3>(&dual)) ++rays;
      else if (CGAL::object_cast<Kernel::Line_3>(&dual)) ++lines;
    }
    std::cout << "dimension: 3\n sites: " << rows.size()
              << "\nfinite Delaunay facets: " << finite_facets
              << "\nVoronoi segments: " << segments << "\nVoronoi rays: " << rays
              << "\nVoronoi lines: " << lines << '\n';
  }
}
