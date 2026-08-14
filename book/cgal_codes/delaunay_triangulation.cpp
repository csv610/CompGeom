#include "point_io.h"
#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Object.h>

#include <iostream>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Point = Kernel::Point_2;
using Segment = Kernel::Segment_2;
using Ray = Kernel::Ray_2;
using Line = Kernel::Line_2;
using Delaunay = CGAL::Delaunay_triangulation_2<Kernel>;

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: delaunay_triangulation points.txt\n";
    return 2;
  }
  std::vector<Point> points;
  try {
    points = compgeom::read_points_2d<Point>(argv[1]);
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }

  Delaunay triangulation;
  triangulation.insert(points.begin(), points.end());

  std::cout << "vertices: " << triangulation.number_of_vertices() << '\n';
  std::cout << "finite faces: " << triangulation.number_of_faces() << '\n';

  std::size_t edge_count = 0;
  for (auto edge = triangulation.finite_edges_begin();
       edge != triangulation.finite_edges_end(); ++edge) {
    ++edge_count;
  }
  std::cout << "finite edges: " << edge_count << '\n';

  std::cout << "Voronoi duals of finite edges:\n";
  for (auto edge = triangulation.finite_edges_begin();
       edge != triangulation.finite_edges_end(); ++edge) {
    const CGAL::Object dual = triangulation.dual(*edge);
    if (const auto* segment = CGAL::object_cast<Segment>(&dual)) {
      std::cout << "segment " << *segment << '\n';
    } else if (const auto* ray = CGAL::object_cast<Ray>(&dual)) {
      std::cout << "ray " << *ray << '\n';
    } else if (const auto* line = CGAL::object_cast<Line>(&dual)) {
      std::cout << "line " << *line << '\n';
    }
  }
  return 0;
}
