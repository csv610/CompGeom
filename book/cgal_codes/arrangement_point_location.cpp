#include <CGAL/Arr_naive_point_location.h>
#include <CGAL/Arr_segment_traits_2.h>
#include <CGAL/Arrangement_2.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Object.h>

#include <iostream>

using Kernel = CGAL::Exact_predicates_exact_constructions_kernel;
using Traits = CGAL::Arr_segment_traits_2<Kernel>;
using Arrangement = CGAL::Arrangement_2<Traits>;
using Point = Kernel::Point_2;
using Segment = Kernel::Segment_2;

int main() {
  Arrangement arrangement;
  CGAL::insert(arrangement, Segment(Point(0, 0), Point(4, 4)));
  CGAL::insert(arrangement, Segment(Point(0, 4), Point(4, 0)));
  CGAL::insert(arrangement, Segment(Point(2, -1), Point(2, 5)));

  CGAL::Arr_naive_point_location<Arrangement> location(arrangement);
  const CGAL::Object query = location.locate(Point(1, 1));
  Arrangement::Face_const_handle face;
  Arrangement::Halfedge_const_handle halfedge;
  Arrangement::Vertex_const_handle vertex;
  const char* feature = "unknown";
  if (CGAL::assign(face, query)) {
    feature = "face";
  } else if (CGAL::assign(halfedge, query)) {
    feature = "edge";
  } else if (CGAL::assign(vertex, query)) {
    feature = "vertex";
  }

  std::cout << "vertices: " << arrangement.number_of_vertices() << '\n';
  std::cout << "edges: " << arrangement.number_of_edges() << '\n';
  std::cout << "faces: " << arrangement.number_of_faces() << '\n';
  std::cout << "query (1,1) located in arrangement feature: " << feature
            << '\n';
  return 0;
}
