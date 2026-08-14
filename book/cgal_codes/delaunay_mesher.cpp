#include "point_io.h"

#include <CGAL/Constrained_Delaunay_triangulation_2.h>
#include <CGAL/Delaunay_mesh_face_base_2.h>
#include <CGAL/Delaunay_mesh_size_criteria_2.h>
#include <CGAL/Delaunay_mesh_vertex_base_2.h>
#include <CGAL/Delaunay_mesher_2.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangulation_data_structure_2.h>

#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;

int main(int argc, char** argv) {
  if (argc < 2 || argc > 3) {
    std::cerr << "usage: delaunay_mesher points.{txt,obj,off} [max_edge_for_2d]\n";
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
    using Vb = CGAL::Delaunay_mesh_vertex_base_2<Kernel>;
    using Fb = CGAL::Delaunay_mesh_face_base_2<Kernel>;
    using Tds = CGAL::Triangulation_data_structure_2<Vb, Fb>;
    using Tr = CGAL::Constrained_Delaunay_triangulation_2<Kernel, Tds>;
    using Criteria = CGAL::Delaunay_mesh_size_criteria_2<Tr>;
    std::vector<Kernel::Point_2> points;
    points.reserve(rows.size());
    for (const auto& row : rows) points.emplace_back(row[0], row[1]);
    Tr triangulation;
    triangulation.insert(points.begin(), points.end());
    if (argc == 3) {
      const double max_edge = std::stod(argv[2]);
      if (!(max_edge > 0.0)) throw std::invalid_argument("max_edge must be positive");
      CGAL::Delaunay_mesher_2<Tr, Criteria> mesher(
          triangulation, Criteria(0.125, max_edge));
      mesher.init(false);
      mesher.refine_mesh();
    }
    std::cout << "dimension: 2\ninput points: " << rows.size()
              << "\nvertices: " << triangulation.number_of_vertices()
              << "\nfinite faces: " << triangulation.number_of_faces()
              << "\nrefined: " << (argc == 3 ? "true" : "false") << '\n';
  } else {
    if (argc == 3) {
      std::cerr << "max_edge refinement is supported only for 2D input\n";
      return 2;
    }
    std::vector<Kernel::Point_3> points;
    points.reserve(rows.size());
    for (const auto& row : rows) points.emplace_back(row[0], row[1], row[2]);
    CGAL::Delaunay_triangulation_3<Kernel> triangulation;
    triangulation.insert(points.begin(), points.end());
    std::cout << "dimension: 3\ninput points: " << rows.size()
              << "\nvertices: " << triangulation.number_of_vertices()
              << "\nfinite cells: " << triangulation.number_of_finite_cells() << '\n';
  }
}
